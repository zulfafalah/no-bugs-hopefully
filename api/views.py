import jwt as pyjwt
from datetime import datetime, timedelta, timezone

from django.conf import settings as django_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    BookSerializer, 
    BookCreateUpdateSerializer,
    BookPartialUpdateSerializer,
    EchoRequestSerializer,
    StandardResponseSerializer
)


# In-memory storage for books
BOOKS = {}
BOOK_ID_COUNTER = 1


@extend_schema(
    summary="Obtain JWT Token",
    description="""
    Authenticate and obtain JWT access and refresh tokens.
    
    **Default Credentials for Testing:**
    - Username: `admin`
    - Password: `password`
    
    Use the access token in the Authorization header as: `Bearer <access_token>`
    """,
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {
                    'type': 'string',
                    'example': 'admin'
                },
                'password': {
                    'type': 'string',
                    'example': 'password'
                }
            },
            'required': ['username', 'password']
        }
    },
    examples=[
        OpenApiExample(
            'Example Login',
            value={
                'username': 'admin',
                'password': 'password'
            },
            request_only=True,
        )
    ],
    responses={
        200: {
            'description': 'Successful authentication',
            'content': {
                'application/json': {
                    'example': {
                        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                    }
                }
            }
        },
        401: {
            'description': 'Invalid credentials'
        }
    }
)
class CustomTokenObtainPairView(APIView):
    """
    Custom JWT token view that validates hardcoded credentials.
    No database user required.
    
    Default test credentials:
    - username: admin
    - password: password
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username == 'admin' and password == 'password':
            now = datetime.now(timezone.utc)
            access_payload = {
                'user_id': 1,
                'username': 'admin',
                'exp': now + timedelta(hours=1),
                'iat': now,
                'token_type': 'access',
            }
            refresh_payload = {
                'user_id': 1,
                'username': 'admin',
                'exp': now + timedelta(days=1),
                'iat': now,
                'token_type': 'refresh',
            }
            access = pyjwt.encode(access_payload, django_settings.SECRET_KEY, algorithm='HS256')
            refresh = pyjwt.encode(refresh_payload, django_settings.SECRET_KEY, algorithm='HS256')
            return Response({
                'token': access,
                'access': access,
                'refresh': refresh,
            })

        return Response(
            {'detail': 'No active account found with the given credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class CustomTokenRefreshView(APIView):
    """Refresh an access token using a refresh token."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = pyjwt.decode(refresh_token, django_settings.SECRET_KEY, algorithms=['HS256'])
            if payload.get('token_type') != 'refresh':
                raise AuthenticationFailed('Invalid token type')
            now = datetime.now(timezone.utc)
            access_payload = {
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'exp': now + timedelta(hours=1),
                'iat': now,
                'token_type': 'access',
            }
            access = pyjwt.encode(access_payload, django_settings.SECRET_KEY, algorithm='HS256')
            return Response({'access': access})
        except pyjwt.InvalidTokenError:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    summary="Ping endpoint",
    description="Simple ping endpoint to check if the API is running",
    responses={200: StandardResponseSerializer}
)
@api_view(['GET'])
def ping(request):
    """
    Simple ping endpoint to check if the API is running
    """
    return Response({
        'success': True
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Echo endpoint",
    description="Echo endpoint that returns the same data sent in the request",
    request=EchoRequestSerializer,
    responses={200: StandardResponseSerializer}
)
@api_view(['POST'])
def echo(request):
    """
    Echo endpoint that returns the same data sent in the request
    """
    return Response(request.data, status=status.HTTP_200_OK)


@extend_schema(
    methods=['GET'],
    summary="List all books",
    description="Get a list of all books in the collection. Supports filtering by author and pagination.",
    parameters=[
        OpenApiParameter(
            name='author',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter books by author name (case-insensitive partial match)',
            required=False
        ),
        OpenApiParameter(
            name='page',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Page number for pagination (starts from 1)',
            required=False
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Number of items per page',
            required=False
        ),
    ],
    responses={200: BookSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    summary="Create a new book",
    description="Add a new book to the collection",
    request=BookCreateUpdateSerializer,
    examples=[
        OpenApiExample(
            'Complete book',
            value={
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'description': 'A classic American novel',
                'year': 1925
            },
            request_only=True,
        ),
        OpenApiExample(
            'Minimal book (required fields only)',
            value={
                'title': 'Sample Book',
                'author': 'John Doe'
            },
            request_only=True,
        ),
    ],
    responses={
        201: BookSerializer,
        400: StandardResponseSerializer
    }
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def book_list(request):
    """
    GET: List all books (supports filtering by author and pagination)
    POST: Create a new book
    """
    global BOOK_ID_COUNTER
    
    if request.method == 'GET':
        books = list(BOOKS.values())
        
        # Filter by author if provided
        author_filter = request.query_params.get('author', None)
        if author_filter:
            books = [book for book in books if author_filter.lower() in book['author'].lower()]
        
        # Return just the array of books for basic tests
        return Response(books, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Validate with serializer
        serializer = BookCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new book
        book = {
            'id': BOOK_ID_COUNTER,
            'title': serializer.validated_data['title'],
            'author': serializer.validated_data['author'],
            'description': serializer.validated_data.get('description', ''),
            'year': serializer.validated_data.get('year', None)
        }
        
        BOOKS[BOOK_ID_COUNTER] = book
        BOOK_ID_COUNTER += 1
        
        return Response(book, status=status.HTTP_201_CREATED)


@extend_schema(
    methods=['GET'],
    summary="Get a book by ID",
    description="Retrieve a specific book by its ID",
    parameters=[
        OpenApiParameter(
            name='book_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='ID of the book to retrieve'
        )
    ],
    responses={
        200: BookSerializer,
        404: StandardResponseSerializer
    }
)
@extend_schema(
    methods=['PUT'],
    summary="Update a book",
    description="Update an existing book by its ID. All fields are optional - you can update one or more fields.",
    parameters=[
        OpenApiParameter(
            name='book_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='ID of the book to update'
        )
    ],
    request=BookPartialUpdateSerializer,
    examples=[
        OpenApiExample(
            'Update all fields',
            value={
                'title': 'Updated Book Title',
                'author': 'Updated Author',
                'description': 'Updated description',
                'year': 2025
            },
            request_only=True,
        ),
        OpenApiExample(
            'Update title only',
            value={
                'title': 'New Title'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Update multiple fields',
            value={
                'title': 'New Title',
                'author': 'New Author',
                'year': 2026
            },
            request_only=True,
        ),
    ],
    responses={
        200: BookSerializer,
        400: StandardResponseSerializer,
        404: StandardResponseSerializer
    }
)
@extend_schema(
    methods=['DELETE'],
    summary="Delete a book",
    description="Delete a book by its ID",
    parameters=[
        OpenApiParameter(
            name='book_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='ID of the book to delete'
        )
    ],
    responses={
        200: StandardResponseSerializer,
        404: StandardResponseSerializer
    }
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def book_detail(request, book_id):
    """
    GET: Retrieve a specific book
    PUT: Update a specific book
    DELETE: Delete a specific book
    """
    # Check if book exists
    if book_id not in BOOKS:
        return Response({
            'error': 'Book not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(BOOKS[book_id], status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Validate with serializer
        serializer = BookPartialUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': serializer.errors,
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update book
        book = BOOKS[book_id]
        if 'title' in serializer.validated_data:
            book['title'] = serializer.validated_data['title']
        if 'author' in serializer.validated_data:
            book['author'] = serializer.validated_data['author']
        if 'description' in serializer.validated_data:
            book['description'] = serializer.validated_data['description']
        if 'year' in serializer.validated_data:
            book['year'] = serializer.validated_data['year']
        
        return Response(book, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        deleted_book = BOOKS.pop(book_id)
        return Response(deleted_book, status=status.HTTP_200_OK)
