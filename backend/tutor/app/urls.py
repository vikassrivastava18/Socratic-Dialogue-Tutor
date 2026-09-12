from django.urls import path

from .views import (
	ChatQueryView,
    CodingProblemListView,
    CodingProblemCreateView,
    CodeSnippetDetailView,
    QuizCreateView,
    QuizEvaluationView,
    QuizListView,
    SubTopicDetailView,
    TopicDetailView,
    TopicListView,
)

# Topics URL
urlpatterns = [
    path('topics/', TopicListView.as_view(), name='topic-list'),
    path('topics/<int:pk>/', TopicDetailView.as_view(), name='topic-detail'),    
    path('code-snippets/<int:pk>/', CodeSnippetDetailView.as_view(), name='code-snippet-detail'),
]

# Subtopics URL
urlpatterns += [
    path('subtopics/<int:pk>/', SubTopicDetailView.as_view(), name='subtopic-detail'),
	path('subtopics/<int:subtopic_id>/quizzes/', QuizListView.as_view(), name='subtopic-quizzes'),
    path('subtopics/<int:subtopic_id>/coding-problems/', CodingProblemListView.as_view(), name='subtopic-coding-problems-list'),
    path('subtopics/<int:subtopic_id>/quizzes/evaluate/', QuizEvaluationView.as_view(), name='subtopic-quiz-evaluate'),
    path('subtopics/<int:subtopic_id>/chat/', ChatQueryView.as_view(), name='subtopic-chat'),
    path('subtopics/<int:subtopic_id>/quiz-create/', QuizCreateView.as_view(), name='subtopic-quiz'),
    path('subtopics/<int:subtopic_id>/coding-problems-create/', CodingProblemCreateView.as_view(), name='subtopic-coding-problems'),
]
