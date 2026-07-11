from django.urls import path
from .views import CreateAppointmentView, CancelAppointmentView, MyAppointmentsView, ConfirmAppointmentView, PayAppointmentView, ProviderAppointmentsView

urlpatterns = [
    path('', CreateAppointmentView.as_view(), name='create-appointment'),
    path('my/', MyAppointmentsView.as_view(), name='my-appointments'),
    path('provider/', ProviderAppointmentsView.as_view(), name='provider-appointments'),
    path('<int:id>/cancel/', CancelAppointmentView.as_view(), name='cancel-appointment'),
    path('<int:id>/confirm/', ConfirmAppointmentView.as_view(), name='confirm-appointment'),
    path('<int:id>/pay/', PayAppointmentView.as_view(), name='pay-appointment'),
]
