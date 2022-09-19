from django.urls import path

from . import views

app_name = "chores"
urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.add_chore, name="add_chore"),
    path("chores/<int:chore_id>/edit", views.edit_chore, name="edit_chore"),
    path("chores/<int:chore_id>/delete",
         views.delete_chore, name="delete_chore"),
]
