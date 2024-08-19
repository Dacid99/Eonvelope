from django.contrib.auth.models import AbstractUser

class UserModel(AbstractUser):
    
    class Meta:
        db_table = "users"