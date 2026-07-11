from django.urls import path
from .views import (
    ServiceListView, CategoryListView, ServiceDetailView,
    CreateServiceView, MyServicesView, ServiceManageView,
    ProviderDashboardView, ServiceUpdateView,
    AdminCategoryCreateView, AdminCategoryDeleteView,
)

urlpatterns = [
    path('', ServiceListView.as_view(), name='service-list'),
    path('categories/', CategoryListView.as_view(), name='service-categories'),
    path('categories/add/', AdminCategoryCreateView.as_view(), name='cat-add'),
    path('categories/<int:cat_id>/delete/', AdminCategoryDeleteView.as_view(), name='cat-delete'),
    path('<int:id>/', ServiceDetailView.as_view(), name='service-detail'),
    path('publish/', CreateServiceView.as_view(), name='service-publish'),
    path('my/', MyServicesView.as_view(), name='my-services'),
    path('manage/<int:id>/', ServiceManageView.as_view(), name='service-manage'),
    path('dashboard/', ProviderDashboardView.as_view(), name='provider-dashboard'),
    path('<int:service_id>/update/', ServiceUpdateView.as_view(), name='service-update'),
]
