from django.urls import path
from .views import PublicCredentialVerificationView

urlpatterns = [
    path('verify/<uuid:pk>', PublicCredentialVerificationView.as_view(), name='verify-credential'),
]
