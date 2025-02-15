from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def purchase(request):
    pass