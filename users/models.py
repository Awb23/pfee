from django.db import models
from django.contrib.auth.models import AbstractUser
from PPFE.settings import AUTH_USER_MODEL

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
import datetime

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('parent', 'Parent'),
        ('child', 'Child'),
    ]
    birth_date = models.DateField(null=True, blank=True) 
    email = models.EmailField(max_length=254, unique=True)
    is_parent = models.BooleanField(default=False)
    is_child = models.BooleanField(default=False)
    role = models.CharField(choices=ROLE_CHOICES, max_length=10)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children_users'
    )
    invitation_code = models.CharField(max_length=36, null=True, blank=True, unique=True)  # كود UUID

    def generate_invitation_code(self):
        if self.is_child and not self.invitation_code:
            self.invitation_code = str(uuid.uuid4())  # توليد كود عشوائي
            self.save()
        return self.invitation_code
    def calculate_age(self):
        """حساب العمر تلقائيًا من تاريخ الميلاد"""
        if self.birth_date:
            today = datetime.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None  # إذا لم يتم إدخال تاريخ ميلاد

    def __str__(self):
        return self.username





class Parent(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='parent_profile')  # Referencing CustomUser
    
    def __str__(self):
        return self.user.username


class Child(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='child_profile')  # Referencing CustomUser
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name="children")

    def __str__(self):
        return self.user.username
