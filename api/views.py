from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def ping(request):
    """
    Simple ping endpoint to check if the API is running
    """
    return Response({
        'message': 'pong',
        'status': 'success'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def echo(request):
    """
    Echo endpoint that returns the same data sent in the request
    """
    return Response({
        'data': request.data,
        'status': 'success'
    }, status=status.HTTP_200_OK)
