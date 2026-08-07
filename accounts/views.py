from accounts.serializers import SignUpSerializer, LoginSerializer

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


@swagger_auto_schema(
    method='post',
    operation_summary='Register a new user',
    operation_description='Creates a new user account with the role "Member" and "Active" status by default. ',
    request_body=SignUpSerializer,
    tags=['Authentication'],
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


@swagger_auto_schema(
    method='post',
    operation_summary='User login',
    operation_description='Authenticates a user and returns JWT tokens.',
    request_body=LoginSerializer,
    tags=['Authentication'],
)
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            tokens = serializer.validated_data

            return Response({
                'message': 'Login successful',
                'tokens': tokens
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Login failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_summary='Refresh access token',
    operation_description='Exchanges a valid refresh token for a new access token (and a new refresh token, since rotation is enabled).',
    request_body=TokenRefreshSerializer,
    tags=['Authentication'],
)
@api_view(['POST'])
def refresh(request):
    if request.method == 'POST':
        serializer = TokenRefreshSerializer(data=request.data)

        try:
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            errors = serializer.errors
        except TokenError as e:
            errors = {'refresh': [str(e)]}

        return Response({
            'message': 'Token refresh failed',
            'errors': errors
        }, status=status.HTTP_400_BAD_REQUEST)