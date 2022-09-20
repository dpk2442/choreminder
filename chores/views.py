from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import (get_list_or_404, get_object_or_404, redirect,
                              render, resolve_url)

from chores import forms, models


@login_required
def index(request: HttpRequest):
    chores = models.Chore.objects.all().order_by("id")
    return render(request, "chores/index.html", dict(
        title="Chores",
        chores=chores,
    ))


@login_required
def add_chore(request: HttpRequest):
    if request.method == "POST":
        form = forms.ChoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("chores:index")
    else:
        form = forms.ChoreForm()

    return render(request, "chores/chore_form.html", dict(
        title="Add Chore",
        url=resolve_url("chores:add_chore"),
        form=form,
    ))


@login_required
def edit_chore(request: HttpRequest, chore_id: int):
    chore = get_object_or_404(models.Chore, pk=chore_id)
    if request.method == "POST":
        form = forms.ChoreForm(request.POST, instance=chore)
        if form.is_valid():
            form.save()
            return redirect("chores:index")
    else:
        form = forms.ChoreForm(instance=chore)

    return render(request, "chores/chore_form.html", dict(
        title="Edit Chore",
        url=resolve_url("chores:edit_chore", chore_id),
        form=form,
    ))


@login_required
def delete_chore(request: HttpRequest, chore_id: int):
    chore = get_object_or_404(models.Chore, pk=chore_id)
    if request.method == "POST":
        chore.delete()
        return redirect("chores:index")

    return render(request, "chores/chore_delete.html", dict(
        title="Delete Chore",
        chore=chore,
    ))
