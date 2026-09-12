from django.urls import path
from .views import QuizCreateView, CodingProblemCreateView

urlpatterns = [
    path('subtopics/<int:subtopic_id>/quiz-create/', QuizCreateView.as_view(), name='subtopic-quiz'),
    path('subtopics/<int:subtopic_id>/coding-problems-create/', CodingProblemCreateView.as_view(), name='subtopic-coding-problems'),
]