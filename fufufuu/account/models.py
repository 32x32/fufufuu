from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from fufufuu.core.uploads import user_avatar_upload_to


class UserManager(BaseUserManager):

    def create_superuser(self, username, password, **kwargs):
        user = self.model(username=username, is_staff=True, is_active=True, **kwargs)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser):

    username            = models.CharField(max_length=30, unique=True)
    email               = models.EmailField(max_length=254, blank=True)
    markdown            = models.TextField(blank=True)
    html                = models.TextField(blank=True)
    avatar              = models.FileField(upload_to=user_avatar_upload_to, blank=True, null=True)
    is_staff            = models.BooleanField(default=False)
    is_active           = models.BooleanField(default=True)

    # 24 hour limits
    upload_limit        = models.IntegerField(default=10)
    comment_limit       = models.IntegerField(default=100)

    created_on          = models.DateTimeField(auto_now_add=True)
    updated_on          = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def get_short_name(self):   return self.username
    def get_full_name(self):    return self.username

    def has_perm(self, perm, obj=None):     return True
    def has_module_perms(self, app_label):  return True

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'
