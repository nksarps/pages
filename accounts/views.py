from accounts.serializers import SignUpSerializer

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@swagger_auto_schema(
    method='post',
    operation_summary='Register a new user',
    operation_description='Creates a new user account with the role "Member" and "Active" status by default. ',
    request_body=SignUpSerializer,
)
@api_view(['POST'])
def sign_up(request):
    if request.method == 'POST':
        serializer = SignUpSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({
                'message': 'User created successfully',
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'message': 'User creation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)