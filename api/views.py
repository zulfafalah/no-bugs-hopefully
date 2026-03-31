from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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
        'message': 'pong',
        'status': 'success'
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
    return Response({
        'data': request.data,
        'status': 'success'
    }, status=status.HTTP_200_OK)


@extend_schema(
    methods=['GET'],
    summary="List all books",
    description="Get a list of all books in the collection",
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
                'published_year': 1925
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
    GET: List all books
    POST: Create a new book
    """
    global BOOK_ID_COUNTER
    
    if request.method == 'GET':
        books = list(BOOKS.values())
        return Response({
            'data': books,
            'count': len(books),
            'status': 'success'
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Validate with serializer
        serializer = BookCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': serializer.errors,
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new book
        book = {
            'id': BOOK_ID_COUNTER,
            'title': serializer.validated_data['title'],
            'author': serializer.validated_data['author'],
            'description': serializer.validated_data.get('description', ''),
            'published_year': serializer.validated_data.get('published_year', None)
        }
        
        BOOKS[BOOK_ID_COUNTER] = book
        BOOK_ID_COUNTER += 1
        
        return Response({
            'data': book,
            'status': 'success'
        }, status=status.HTTP_201_CREATED)


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
                'published_year': 2025
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
                'published_year': 2026
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
def book_detail(request, book_id):
    """
    GET: Retrieve a specific book
    PUT: Update a specific book
    DELETE: Delete a specific book
    """
    # Check if book exists
    if book_id not in BOOKS:
        return Response({
            'error': 'Book not found',
            'status': 'error'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response({
            'data': BOOKS[book_id],
            'status': 'success'
        }, status=status.HTTP_200_OK)
    
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
        if 'published_year' in serializer.validated_data:
            book['published_year'] = serializer.validated_data['published_year']
        
        return Response({
            'data': book,
            'status': 'success'
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        deleted_book = BOOKS.pop(book_id)
        return Response({
            'data': deleted_book,
            'message': 'Book deleted successfully',
            'status': 'success'
        }, status=status.HTTP_200_OK)
