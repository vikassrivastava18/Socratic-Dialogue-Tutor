from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Course, SubTopic, Topic


class QuizListViewTests(APITestCase):
	def setUp(self):
		course = Course.objects.create(name='CS50')
		topic = Topic.objects.create(
			title='Python',
			course=course,
			summary='Python fundamentals',
		)
		self.subtopic = SubTopic.objects.create(
			topic=topic,
			title='Functions',
			summary='Function fundamentals',
			quizzes={
				'mcq': [{'question': 'What is a function?'}],
				'true_false': [],
				'fill_blank': [],
			},
		)

	def test_returns_subtopic_quizzes(self):
		response = self.client.get(
			reverse('subtopic-quizzes', kwargs={'subtopic_id': self.subtopic.pk})
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), self.subtopic.quizzes)

	def test_returns_not_found_for_unknown_subtopic(self):
		response = self.client.get(
			reverse('subtopic-quizzes', kwargs={'subtopic_id': 9999})
		)

		self.assertEqual(response.status_code, 404)


class QuizEvaluationViewTests(APITestCase):
	def setUp(self):
		course = Course.objects.create(name='CS50')
		topic = Topic.objects.create(
			title='Python',
			course=course,
			summary='Python fundamentals',
		)
		self.subtopic = SubTopic.objects.create(
			topic=topic,
			title='Functions',
			summary='Function fundamentals',
			quizzes={
				'mcq': [{
					'question': 'What is a function?',
					'answer': 'A reusable block',
					'explanation': 'Functions can be called repeatedly.',
				}],
				'true_false': [{
					'question': 'Functions can take arguments.',
					'answer': True,
					'explanation': 'Arguments provide input.',
				}],
				'fill_blank': [{
					'quiz': 'A function is defined with the ___ keyword.',
					'answer': 'def',
				}],
			},
		)

	def test_evaluates_answers(self):
		response = self.client.post(
			reverse(
				'subtopic-quiz-evaluate',
				kwargs={'subtopic_id': self.subtopic.pk},
			),
			{
				'answers': {
					'mcq': ['a reusable block'],
					'true_false': [False],
					'fill_blank': [' DEF '],
				},
			},
			format='json',
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['score'], 2)
		self.assertEqual(response.json()['total'], 3)
		self.assertEqual(response.json()['percentage'], 66.67)
		self.assertTrue(response.json()['results']['mcq'][0]['correct'])
		self.assertFalse(response.json()['results']['true_false'][0]['correct'])

	def test_requires_answers_object(self):
		response = self.client.post(
			reverse(
				'subtopic-quiz-evaluate',
				kwargs={'subtopic_id': self.subtopic.pk},
			),
			{},
			format='json',
		)

		self.assertEqual(response.status_code, 400)
