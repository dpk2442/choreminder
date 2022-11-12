from django.urls import path

from . import views

app_name = "chores"
urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.add_chore, name="add_chore"),
    path("chores/<int:chore_id>/edit", views.edit_chore, name="edit_chore"),
    path("chores/<int:chore_id>/delete",
         views.delete_chore, name="delete_chore"),
    path("chores/<int:chore_id>/logs/add", views.log_chore, name="log_chore"),
    path("categories", views.list_categories, name="list_categories"),
    path("categories/add", views.add_category, name="add_category"),
    path("categories/<int:category_id>/edit",
         views.edit_category, name="edit_category"),
    path("categories/<int:category_id>/delete",
         views.delete_category, name="delete_category"),
]
