from uuid import uuid4

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CodeSnippet, SubTopic, Topic
from .serializers import (
	CodeSnippetSerializer,
	SubTopicSerializer,
	TopicDetailSerializer,
	TopicSerializer,
)
from .utils.agents.ask import TutorGraph
from .utils.agents.quiz import create_quizzes
from .utils.open_ai import llm


def _call_llm(prompt):
	return llm.invoke(prompt)


class TopicListView(generics.ListAPIView):
	queryset = Topic.objects.all()
	serializer_class = TopicSerializer


class TopicDetailView(generics.RetrieveAPIView):
	queryset = Topic.objects.all()
	serializer_class = TopicDetailSerializer


class SubTopicDetailView(generics.RetrieveAPIView):
	queryset = SubTopic.objects.all()
	serializer_class = SubTopicSerializer


class QuizListView(APIView):
	def get(self, request, subtopic_id):
		subtopic = get_object_or_404(SubTopic, pk=subtopic_id)
		return Response(subtopic.quizzes or {})


class CodeSnippetDetailView(generics.RetrieveAPIView):
	queryset = CodeSnippet.objects.all()
	serializer_class = CodeSnippetSerializer


class ChatQueryView(APIView):
	def post(self, request, subtopic_id):
		query = request.data.get('query')
		if not isinstance(query, str) or not query.strip():
			return Response(
				{'query': 'This field is required.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		subtopic = get_object_or_404(SubTopic, pk=subtopic_id)
		thread_id = request.data.get('thread_id') or str(uuid4())
		topic_graph = TutorGraph()
		result = topic_graph.invoke(
			query=query,
			context=subtopic.summary,
			thread_id=thread_id,
		)

		return Response({
			'answer': result['answer'],
			'thread_id': thread_id,
		})


class QuizCreateView(APIView):
	def post(self, request, subtopic_id):
		subtopic = get_object_or_404(SubTopic, pk=subtopic_id)
		quizzes = create_quizzes(subtopic.summary)
		return Response(quizzes.model_dump())


class QuizEvaluationView(APIView):
	def post(self, request, subtopic_id):
		subtopic = get_object_or_404(SubTopic, pk=subtopic_id)
		answers = request.data.get('answers')
		if not isinstance(answers, dict):
			return Response(
				{'answers': 'This field must be an object.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		results, score, total = self._evaulate_response(subtopic, answers)
		response = {
			'score': score,
			'total': total,
			'percentage': round(score / total * 100, 2) if total else 0,
			'results': results,
		} 
		if not score > 7:
			hints = self._get_hints(results)
			response["hints"] = hints
			return Response(response)
		
		return Response(response)


	def _evaulate_response(self, subtopic, answers):
		quizzes = subtopic.quizzes or {}
		results = {}
		score = 0
		total = 0
	
		for category in quizzes.keys():
			category_quizzes = quizzes.get(category, [])
			category_answers = answers.get(category, [])
			if not isinstance(category_answers, list):
				return Response(
					{category: 'Answers must be an array.'},
					status=status.HTTP_400_BAD_REQUEST,
				)

			category_results = []
			for index, quiz in enumerate(category_quizzes):
				submitted_answer = (
					category_answers[index] if index < len(category_answers) else None
				)
				expected_answer = quiz.get('answer')
				is_correct = self._answers_match(
					submitted_answer,
					expected_answer,
				)
				score += int(is_correct)
				total += 1
				category_results.append({
					'question': quiz.get('question', quiz.get('quiz')),
					'submitted_answer': submitted_answer,
					'correct': is_correct,
					'expected_answer': expected_answer,
					'explanation': quiz.get('explanation'),
				})

			results[category] = category_results
		return results, score, total

	@staticmethod
	def _get_hints(results):
		sections = []
		for category, category_results in results.items():
			category_hints = []
			for item in category_results:
				if item.get('correct'):
					continue
				question = item.get('question') or ''
				expected_answer = item.get('expected_answer')
				submitted_answer = item.get('submitted_answer')
				prompt = (
					'You are a helpful tutor. Provide a short hint for a learner who answered a quiz question incorrectly. '
					f'Question: {question}\n'
					f'Submitted answer: {submitted_answer}\n'
					f'Expected answer: {expected_answer}\n'
					'Give only a brief hint without revealing the final answer directly.'
				)
				try:
					hint = _call_llm(prompt)
					if hasattr(hint, 'content'):
						hint = hint.content
					if isinstance(hint, str):
						hint_text = hint.strip()
					else:
						hint_text = str(hint).strip()
				except Exception:
					hint_text = 'Review the key concept from the lesson and try again.'
				category_hints.append(f'- **{question}**: {hint_text}')

			if category_hints:
				category_title = category.replace('_', ' ').title()
				sections.append(f'### {category_title}\n' + '\n'.join(category_hints))

		return '\n\n'.join(sections) if sections else 'No hints available.'

		
	@staticmethod
	def _answers_match(submitted_answer, expected_answer):
		if isinstance(expected_answer, bool):
			return submitted_answer is expected_answer
		if not isinstance(submitted_answer, str) or not isinstance(expected_answer, str):
			return submitted_answer == expected_answer
		return submitted_answer.strip().casefold() == expected_answer.strip().casefold()


