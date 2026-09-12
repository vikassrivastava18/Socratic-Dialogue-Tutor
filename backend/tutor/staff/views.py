from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response

from app.models import SubTopic
from .utils import create_coding_problems, create_quizzes
# Create your views here.


class CodingProblemCreateView(APIView):
	permission_classes = (IsAdminUser,)

	def post(self, request, subtopic_id):
		subtopic = get_object_or_404(SubTopic, pk=subtopic_id)
		codes = create_coding_problems(subtopic.summary).model_dump()
		SubTopic.objects.filter(pk=subtopic.pk).update(codes=codes)
		return Response(codes)


class QuizCreateView(APIView):
	permission_classes = (IsAdminUser,)
	
	def post(self, request, subtopic_id):
		subtopic = get_object_or_404(SubTopic, pk=subtopic_id)
		quizzes = create_quizzes(subtopic.summary)
		return Response(quizzes.model_dump())
