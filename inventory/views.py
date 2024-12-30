from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import InventoryItem, InventoryChangeLog
from .serializers import InventoryItemSerializer, LoginSerializer, UserSerializer, UserProfileSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

def HomeView(request):
    return HttpResponse("Welcome to the Inventory Management API")


# Existing class-based view for listing and creating inventory items

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def getInventoryListView(request):
    items = InventoryItem.objects.all()
    serializer = InventoryItemSerializer(items, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def postInventoryListView(request):
    serializer = InventoryItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# New function-based view for detailed inventory management (retrieve, update, delete)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def inventory_detail(request, pk):
    """
    Retrieve, update, or delete a specific inventory item.
    """
    try:
        item = InventoryItem.objects.get(pk=pk, user=request.user)
    except InventoryItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = InventoryItemSerializer(item)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = InventoryItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# New function-based view for updating inventory quantities
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_quantity(request, pk):
    """
    Update the quantity of an inventory item.
    """
    try:
        item = InventoryItem.objects.get(pk=pk, user=request.user)
    except InventoryItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    added = int(request.data.get('added', 0))
    removed = int(request.data.get('removed', 0))
    item.quantity += added - removed
    item.save()

    # Log the change
    InventoryChangeLog.objects.create(
        inventory_item=item,
        added=added,
        removed=removed,
        user=request.user
    )

    return Response({'message': 'Quantity updated successfully'}, status=status.HTTP_200_OK)


# New function-based view for viewing change logs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def change_log(request):
    """
    View the change log for all inventory items.
    """
    logs = InventoryChangeLog.objects.filter(user=request.user)
    serializer = InventoryChangeLogSerializer(logs, many=True)
    return Response(serializer.data)
@api_view(['POST'])
@permission_classes([AllowAny])
def UserRegistrationView(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'User created successfully',
            'username': user.username,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def LoginPageView(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "detail": "Login successful",
                "token": token.key
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def ProfileView(request):
    user = request.user
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
        
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])  # Corrected to POST
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def LogoutView(request):
    # Check if the user has an auth token
    if request.user.auth_token:
        request.user.auth_token.delete()  # Deactivate the token
        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)
    return Response({"detail": "No active session found"}, status=status.HTTP_400_BAD_REQUEST)
    