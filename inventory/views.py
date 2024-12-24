from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import InventoryItem
from .serializers import InventoryItemSerializer
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

class HomeView(APIView):
    def get(self, request):
        return HttpResponse("<h1>Welcome to the Inventory Management API</h1>")


class InventoryListView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        items = InventoryItem.objects.all()
        serializer = InventoryItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InventoryItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User created successfully',
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        # Fetch the current authenticated user
        user = request.user
        # Serialize the user object
        serializer = UserSerializer(user)
        return Response(serializer.data)

    