from typing import Union

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser


UserType = Union[AbstractBaseUser, AnonymousUser]
