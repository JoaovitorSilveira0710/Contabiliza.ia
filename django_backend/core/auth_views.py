from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate
from core.serializers import UserSerializer
import logging
import json

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Endpoint de login que retorna token"""
    logger.info("Auth login called", extra={"path": request.path})
    
    # Debug: log what we received
    try:
        logger.info(f"Request data: {request.data}")
        logger.info(f"Request POST: {request.POST}")
        logger.info(f"Request body: {request.body[:200]}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Request method: {request.method}")
    except Exception as e:
        logger.error(f"Error logging request: {e}")
    
    # Try to get data from multiple sources
    email = None
    password = None
    
    # Try request.data first (DRF parsed data)
    if request.data:
        email = request.data.get('email')
        password = request.data.get('password')
    
    # Fallback to request.POST
    if not email and not password:
        email = request.POST.get('email')
        password = request.POST.get('password')
    
    # Last resort: parse raw body
    if not email and not password and request.body:
        try:
            body_data = json.loads(request.body)
            email = body_data.get('email')
            password = body_data.get('password')
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON body: {e}")
    
    if not email or not password:
        logger.warning(f"Missing credentials - email: {email}, password: {'***' if password else None}")
        return Response(
            {'error': 'E-mail e password são obrigatórios'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Since AUTH_USER_MODEL uses email as USERNAME_FIELD, authenticate with username=email
    user = authenticate(username=email, password=password)
    
    if user:
        token, created = Token.objects.get_or_create(user=user)
        logger.info("Auth login success", extra={"user": user.pk, "created_token": created})
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    else:
        logger.warning("Auth login failed: invalid credentials", extra={"email": email})
        return Response(
            {'error': 'Credenciais inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
def logout(request):
    """Endpoint de logout que deleta o token"""
    if request.user.is_authenticated:
        try:
            request.user.auth_token.delete()
        except:
            pass
    return Response({'message': 'Logout realizado com sucesso'})


@api_view(['GET'])
@permission_classes([AllowAny])
def check_auth(request):
    """Verificar se usuário está autenticado"""
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': UserSerializer(request.user).data
        })
    return Response({'authenticated': False})
