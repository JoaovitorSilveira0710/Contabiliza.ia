from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from .models import User
from .serializers import UserSerializer, UserListSerializer, ChangePasswordSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        role = self.request.query_params.get('role', None)
        is_active = self.request.query_params.get('is_active', None)
        search = self.request.query_params.get('search', None)
        
        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset.order_by('-date_joined')
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Alterar senha do usuário"""
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # Verificar senha antiga
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Senha antiga incorreta'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Definir nova senha
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({'message': 'Senha alterada com sucesso'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """Alterar papel do usuário"""
        user = self.get_object()
        new_role = request.data.get('role')
        
        if not new_role:
            return Response(
                {'error': 'Campo role é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.role = new_role
        user.save()
        
        return Response({
            'message': 'Papel alterado com sucesso',
            'user': UserSerializer(user).data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estatísticas de usuários"""
        total = User.objects.count()
        active = User.objects.filter(is_active=True).count()
        by_role = User.objects.values('role').annotate(count=Count('id'))
        
        return Response({
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_role': list(by_role)
        })
