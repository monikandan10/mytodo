from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import CreateTaskSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_choices(request):
    choices = {
        'categories': Task.CATEGORY_CHOICES,
        'statuses': Task.STATUS_CHOICES,
        'priorities': Task.PRIORITY_CHOICES
    }
    return Response(choices)

class CreateTask(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Ensure the username is sent and process the user
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Add the user to the request data before passing to the serializer
        request.data['user'] = user.id

        serializer = CreateTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Task created successfully'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
