import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from typing import cast
from rest_framework import  status
from rest_framework.response import Response

from .schemas import QuizSchema


load_dotenv(override=True)

openai_key = os.getenv("OPENAI_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=SecretStr(openai_key) if openai_key else None,
    temperature=0.2,
    max_retries=2,
)


def create_quizzes(content: str) -> QuizSchema:
    prompt = f"""
    You are a quiz master. Use the content of a chapter to create quizzes that help students in their study.
    For MCQ, only one option should be correct.
    Return the response in the format specified.    

    Content: {content}
    """

    structured_llm = llm.with_structured_output(QuizSchema)
    messages = [
        {
            "role": "system",
            "content": prompt
        }
    ]

    response = structured_llm.invoke(messages)
    return cast(QuizSchema, response)


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
                hint = llm.invoke(prompt)
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

		
def _answers_match(submitted_answer, expected_answer):
    if isinstance(expected_answer, bool):
        return submitted_answer is expected_answer
    if not isinstance(submitted_answer, str) or not isinstance(expected_answer, str):
        return submitted_answer == expected_answer
    return submitted_answer.strip().casefold() == expected_answer.strip().casefold()


def _evaulate_response(subtopic, answers):
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
                is_correct = _answers_match(
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


