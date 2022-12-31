from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from chores import actions, forms, models, queries


@login_required
@require_GET
def index(request: HttpRequest):
    tag_form = forms.TagFilterForm(request.user, request.GET)
    tag_id = (tag_form.cleaned_data["tag"].id
              if tag_form.is_valid() and tag_form.cleaned_data["tag"] is not None
              else None)
    chore_groups = actions.get_grouped_sorted_chores(request.user, tag_id)
    return render(request, "chores/index.html", dict(
        title="Chores",
        chore_groups=chore_groups,
        tag_form=tag_form,
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


@login_required
@require_GET
def list_away_dates(request: HttpRequest):
    away_dates = queries.query_away_dates(request.user)
    return render(request, "chores/away_dates/list.html", dict(
        title="Away Dates",
        away_dates=away_dates,
    ))


@login_required
def add_away_date(request: HttpRequest):
    if request.method == "POST":
        form = forms.AwayDateForm(request.POST)
        if form.is_valid():
            away_date = form.save(commit=False)
            away_date.user = request.user
            away_date.save()
            return redirect("chores:list_away_dates")
    else:
        form = forms.AwayDateForm()

    return render(request, "chores/away_dates/form.html", dict(
        title="Add Away Date",
        url=resolve_url("chores:add_away_date"),
        form=form,
    ))


@login_required
def edit_away_date(request: HttpRequest, away_date_id: int):
    away_date = get_object_or_404(
        models.AwayDate, pk=away_date_id, user=request.user)
    if request.method == "POST":
        form = forms.AwayDateForm(request.POST, instance=away_date)
        if form.is_valid():
            form.save()
            return redirect("chores:list_away_dates")
    else:
        form = forms.AwayDateForm(instance=away_date)

    return render(request, "chores/away_dates/form.html", dict(
        title="Edit Away Date",
        url=resolve_url("chores:edit_away_date", away_date_id),
        form=form,
    ))


@login_required
def delete_away_date(request: HttpRequest, away_date_id: int):
    away_date = get_object_or_404(
        models.AwayDate, pk=away_date_id, user=request.user)
    if request.method == "POST":
        away_date.delete()
        return redirect("chores:list_away_dates")

    return render(request, "chores/away_dates/delete.html", dict(
        title="Delete Away Date",
        away_date=away_date,
    ))
