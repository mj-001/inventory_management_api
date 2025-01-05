import json
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import InventoryItem, InventoryChangeLog
from .serializers import InventoryChangeLogSerializer, InventoryItemSerializer, LoginSerializer, UserSerializer, UserProfileSerializer
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
        serializer.save(managed_by=request.user)
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
        item = InventoryItem.objects.get(pk=pk)
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
def update_quantity(request, item_id):
    """
    Update the quantity of an inventory item and log the change.
    """
    try:
        # Retrieve the inventory item based on the pk and ensure it belongs to the current user
        item = InventoryItem.objects.get(pk=item_id, managed_by=request.user)

        # Get the 'added' and 'removed' quantities from the request data
        added = int(request.data.get('added', 0))  # Default to 0 if not provided
        removed = int(request.data.get('removed', 0))  # Default to 0 if not provided

        # Update the quantity (ensure that quantity doesn't go negative)
        new_quantity = item.quantity + added - removed
        if new_quantity < 0:
            return Response({'error': 'Quantity cannot be negative'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the updated quantity to the inventory item
        item.quantity = new_quantity
        item.save()

        # Log the change in the InventoryChangeLog
        InventoryChangeLog.objects.create(
            item=item,
            changed_by=request.user,
            changed_quantities=(added - removed),  # The net change in quantity
        )

        return Response({
            'message': 'Quantity updated successfully',
            'new_quantity': item.quantity
        }, status=status.HTTP_200_OK)

    except InventoryItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)


# New function-based view for viewing change logs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def change_log(request):
    """
    View the change log for all inventory items.
    """
    # Retrieve change logs for the authenticated user
    logs = InventoryChangeLog.objects.filter(changed_by=request.user)

    # If no logs exist, return a 404 response
    if not logs.exists():
        return Response({'error': 'No change logs found for this user.'}, status=status.HTTP_404_NOT_FOUND)

    # Manually format the logs to match the serializer's expected fields
    formatted_logs = []
    for log in logs:
        formatted_log = {
            'field': 'quantity',  # We assume the change is for quantity in this case
            'old_value': log.item.quantity,  # Old value of the inventory item's quantity
            'new_value': log.changed_quantities,  # New value of the changed quantity
            'changed_by': log.changed_by.username if log.changed_by else 'Unknown',  # Username of the person who made the change
            'timestamp': log.time_changed.isoformat()  # Timestamp of the change
        }
        formatted_logs.append(formatted_log)

    # Serialize the formatted logs
    serializer = InventoryChangeLogSerializer(formatted_logs, many=True)

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


@api_view(['POST'])  
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def LogoutView(request):
    # Check if the user has an auth token
    if request.user.auth_token:
        request.user.auth_token.delete()  # Deactivate the token
        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)
    return Response({"detail": "No active session found"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def inventory_item_history(request, item_id):
    """
    Get the history of changes for a specific inventory item.
    """
    try:
        # Retrieve the inventory item based on the item_id and ensure the item belongs to the current user
        item = InventoryItem.objects.get(pk=item_id, managed_by=request.user)

        # Check if the item has a history
        if item.inventory_item_history:
            # Load the history data from the JSON field
            history_data = json.loads(item.inventory_item_history)
        else:
            history_data = []

        # Return the history in the response
        return Response({
            'item_id': item.id,
            'item_name': item.name,
            'history': history_data
        })
    except InventoryItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)


