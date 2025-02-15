from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Chat, Message
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def protected_view(request):
    return Response({'message': 'This is a protected endpoint!'})


@api_view(['POST'])
def send_message(request):
    
    user = request.user  
    user_id = user.id
    content = request.data.get("message")

    if not content:
        return Response({"error": "Message content is required"}, status=status.HTTP_400_BAD_REQUEST)

    chat = user.chat

    human_message = Message.objects.create(chat=chat, sender_type="human", content=content)

    # ---- AI PROCESSING HAPPENS HERE (IMPLEMENT LATER) ----
    
    # Placeholder AI response
    ai_response = "This is a placeholder AI response."

    # Store the AI response
    ai_message = Message.objects.create(chat=chat, sender_type="ai", content=ai_response)

    return Response({
        "chat_id": chat.id,
        "messages": [
            {"type": "human", "content": human_message.content},
            {"type": "ai", "content": ai_message.content}
        ]
    }, status=status.HTTP_200_OK)


from .utils.agent_client import agent_executor
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """Remove a book from a collection."""

    try:
        query = request.data.get('query')


        response = agent_executor.invoke({"input": query})
        print(f"\nQuery: {query}")
        print(f"Response: {response}")
        

        return Response({'message': 'Search results retrieved', 'results': response}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response({'error': 'Internal Error Happened'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    