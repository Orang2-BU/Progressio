from django.urls import path
from .views import CompetencyListView, CompetencyDetailView

urlpatterns = [
    path('', CompetencyListView.as_view(), name='competency-list'),
    path('<int:pk>', CompetencyDetailView.as_view(), name='competency-detail'),
]
