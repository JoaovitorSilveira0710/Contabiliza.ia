from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('master', 'Master'),
        ('admin', 'Administrador'),
        ('accountant', 'Contador'),
        ('assistant', 'Assistente'),
        ('client_view', 'Visualização de Cliente'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='assistant')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
