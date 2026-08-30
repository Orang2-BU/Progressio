from django.urls import path
from .views import CareerTrackListView, CareerTrackDetailView

urlpatterns = [
    path('', CareerTrackListView.as_view(), name='career-track-list'),
    path('<int:pk>', CareerTrackDetailView.as_view(), name='career-track-detail'),
]
