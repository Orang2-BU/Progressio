from django.urls import path
from .views import SkillListView, SkillDetailView, SkillLessonsView

urlpatterns = [
    path('', SkillListView.as_view(), name='skill-list'),
    path('<int:pk>', SkillDetailView.as_view(), name='skill-detail'),
    path('<int:pk>/lessons', SkillLessonsView.as_view(), name='skill-lessons'),
]
