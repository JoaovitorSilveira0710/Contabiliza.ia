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
    
    email = models.EmailField('E-mail', unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='assistant')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
