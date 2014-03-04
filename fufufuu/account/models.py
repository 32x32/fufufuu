from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from fufufuu.core.uploads import user_avatar_upload_to
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.filters import image_resize
from fufufuu.image.models import Image, get_cache_key


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

    # boolean flags
    is_moderator        = models.BooleanField(default=False)
    is_staff            = models.BooleanField(default=False)
    is_active           = models.BooleanField(default=True)

    # 24 hour limits
    revision_limit      = models.IntegerField(default=10)
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

    @property
    def avatar_url(self):
        return image_resize(self.avatar, ImageKeyType.ACCOUNT_AVATAR, self.id)


@receiver(post_save, sender=User)
def manga_post_save(instance, **kwargs):
    Image.objects.filter(key_type=ImageKeyType.ACCOUNT_AVATAR, key_id=instance.id).delete()
    cache.delete(get_cache_key(ImageKeyType.ACCOUNT_AVATAR, instance.id))
