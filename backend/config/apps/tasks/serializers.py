from rest_framework import serializers
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['user', 'task_name', 'task_description', 'task_category', 'task_status', 'task_priority', 'task_due_date']

    def validate_user(self, value):
        user = User.objects.get(username=value)
        return user

    def create(self, validated_data):
        task = Task.objects.create(**validated_data)
        return task
