from django.contrib import admin

from . import models

admin.site.register(models.Chore)
admin.site.register(models.Log)
admin.site.register(models.Tag)
