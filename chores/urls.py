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
    path("tags", views.list_tags, name="list_tags"),
    path("tags/add", views.add_tag, name="add_tag"),
    path("tags/<int:tag_id>/edit", views.edit_tag, name="edit_tag"),
    path("tags/<int:tag_id>/delete", views.delete_tag, name="delete_tag"),
    path("away-dates", views.list_away_dates, name="list_away_dates"),
    path("away-dates/add", views.add_away_date, name="add_away_date"),
    path("away-dates/<int:away_date_id>/edit",
         views.edit_away_date, name="edit_away_date"),
    path("away-dates/<int:away_date_id>/delete",
         views.delete_away_date, name="delete_away_date"),
]
