from django.urls import path
from .views import get_choices, CreateTask

urlpatterns = [
    path('get-choices/', get_choices, name='get_choices'),
    path('add-task/', CreateTask.as_view(), name='get_choices')
]
