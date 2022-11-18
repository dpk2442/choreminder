from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from chores import actions, forms, models, queries


@login_required
@require_GET
def index(request: HttpRequest):
    chores = actions.get_sorted_chores(request.user)
    return render(request, "chores/index.html", dict(
        title="Chores",
        chores=chores,
    ))


@login_required
def add_chore(request: HttpRequest):
    if request.method == "POST":
        form = forms.ChoreForm(request.user, request.POST)
        if form.is_valid():
            chore = form.save(commit=False)
            chore.user = request.user
            chore.save()
            return redirect("chores:index")
    else:
        form = forms.ChoreForm(request.user)

    return render(request, "chores/chore_form.html", dict(
        title="Add Chore",
        url=resolve_url("chores:add_chore"),
        form=form,
    ))


@login_required
def edit_chore(request: HttpRequest, chore_id: int):
    chore = get_object_or_404(models.Chore, pk=chore_id, user=request.user)
    if request.method == "POST":
        form = forms.ChoreForm(request.user, request.POST, instance=chore)
        if form.is_valid():
            form.save()
            return redirect("chores:index")
    else:
        form = forms.ChoreForm(request.user, instance=chore)

    return render(request, "chores/chore_form.html", dict(
        title="Edit Chore",
        url=resolve_url("chores:edit_chore", chore_id),
        form=form,
    ))


@login_required
def delete_chore(request: HttpRequest, chore_id: int):
    chore = get_object_or_404(models.Chore, pk=chore_id, user=request.user)
    if request.method == "POST":
        chore.delete()
        return redirect("chores:index")

    return render(request, "chores/chore_delete.html", dict(
        title="Delete Chore",
        chore=chore,
    ))


@login_required
@require_POST
def log_chore(request: HttpRequest, chore_id: int):
    chore = get_object_or_404(models.Chore, pk=chore_id, user=request.user)
    models.Log.objects.create(timestamp=timezone.now(),
                              chore=chore, user=request.user)
    return redirect("chores:index")


@login_required
@require_GET
def list_tags(request: HttpRequest):
    tags = queries.query_tags(request.user)
    return render(request, "chores/tags/list.html", dict(
        title="Tags",
        tags=tags,
    ))


@login_required
def add_tag(request: HttpRequest):
    if request.method == "POST":
        form = forms.TagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = request.user
            tag.save()
            return redirect("chores:list_tags")
    else:
        form = forms.TagForm()

    return render(request, "chores/tags/form.html", dict(
        title="Add tag",
        url=resolve_url("chores:add_tag"),
        form=form,
    ))


@login_required
def edit_tag(request: HttpRequest, tag_id: int):
    tag = get_object_or_404(
        models.Tag, pk=tag_id, user=request.user)
    if request.method == "POST":
        form = forms.TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return redirect("chores:list_tags")
    else:
        form = forms.TagForm(instance=tag)

    return render(request, "chores/tags/form.html", dict(
        title="Edit tag",
        url=resolve_url("chores:edit_tag", tag_id),
        form=form,
    ))


@login_required
def delete_tag(request: HttpRequest, tag_id: int):
    tag = get_object_or_404(
        models.Tag, pk=tag_id, user=request.user)
    if request.method == "POST":
        tag.delete()
        return redirect("chores:list_tags")

    return render(request, "chores/tags/delete.html", dict(
        title="Delete tag",
        tag=tag,
    ))
