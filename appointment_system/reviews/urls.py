from django.urls import path
from .views import CreateReviewView, ServiceReviewsView

urlpatterns = [
    path('', CreateReviewView.as_view(), name='create-review'),
    path('service/<int:service_id>/', ServiceReviewsView.as_view(), name='service-reviews'),
]
