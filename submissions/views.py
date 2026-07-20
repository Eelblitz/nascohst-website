from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render

from researchers.models import Researcher

from .forms import SubmissionForm, SubmissionAuthorForm, SubmissionFileForm
from .models import Submission, SubmissionAuthor, SubmissionFile


SubmissionAuthorFormSet = inlineformset_factory(
    Submission,
    SubmissionAuthor,
    form=SubmissionAuthorForm,
    fields=[
        "researcher",
        "staff",
        "external_name",
        "author_order",
        "is_primary",
        "is_corresponding",
        "affiliation",
        "email",
        "orcid",
    ],
    extra=1,
    can_delete=True,
)

SubmissionFileFormSet = inlineformset_factory(
    Submission,
    SubmissionFile,
    form=SubmissionFileForm,
    fields=["file", "file_type", "description"],
    extra=1,
    can_delete=True,
)


def _get_researcher_profile(user):
    return Researcher.objects.filter(user=user).select_related("staff").first()


def _submission_belongs_to_user(submission, user):
    researcher = _get_researcher_profile(user)
    if researcher and submission.authors.filter(researcher=researcher).exists():
        return True
    return False


@login_required
def submission_dashboard(request):
    researcher = _get_researcher_profile(request.user)
    if not researcher:
        raise PermissionDenied("You do not have a researcher profile.")

    submissions = (
        Submission.objects.filter(authors__researcher=researcher)
        .distinct()
        .prefetch_related("authors", "files")
        .order_by("-updated_at", "-submitted_at")
    )

    return render(
        request,
        "submissions/submission_dashboard.html",
        {
            "submissions": submissions,
            "researcher": researcher,
        },
    )


@login_required
def submission_create(request):
    researcher = _get_researcher_profile(request.user)
    if not researcher:
        raise PermissionDenied("You do not have a researcher profile.")

    submission = Submission()

    if request.method == "POST":
        form = SubmissionForm(request.POST, instance=submission)
        author_formset = SubmissionAuthorFormSet(request.POST, instance=submission, prefix="authors")
        file_formset = SubmissionFileFormSet(request.POST, request.FILES, instance=submission, prefix="files")

        if form.is_valid() and author_formset.is_valid() and file_formset.is_valid():
            submission = form.save(commit=False)
            submission.status = Submission.DRAFT if submission.status == Submission.DRAFT else submission.status
            submission.save()

            author_formset.instance = submission
            authors = author_formset.save(commit=False)
            for author in authors:
                if not author.researcher_id and not author.staff_id and not author.external_name:
                    author.researcher = researcher
                author.submission = submission
                author.save()
            for author in author_formset.deleted_objects:
                author.delete()

            file_formset.instance = submission
            file_formset.save()

            if submission.status == Submission.SUBMITTED:
                messages.success(request, "Your manuscript has been submitted.")
            else:
                messages.success(request, "Draft saved successfully.")
            return redirect("submissions:submission_success")
    else:
        form = SubmissionForm(instance=submission, initial={"status": Submission.DRAFT})
        author_formset = SubmissionAuthorFormSet(instance=submission, prefix="authors")
        file_formset = SubmissionFileFormSet(instance=submission, prefix="files")

    return render(
        request,
        "submissions/submission_form.html",
        {
            "form": form,
            "author_formset": author_formset,
            "file_formset": file_formset,
            "submission": submission,
            "mode": "create",
        },
    )


@login_required
def submission_edit(request, pk):
    researcher = _get_researcher_profile(request.user)
    submission = get_object_or_404(Submission, pk=pk)

    if not researcher or not _submission_belongs_to_user(submission, request.user):
        raise PermissionDenied("You do not have permission to edit this submission.")

    if submission.status != Submission.DRAFT:
        raise PermissionDenied("Submitted manuscripts are read-only for now.")

    if request.method == "POST":
        form = SubmissionForm(request.POST, instance=submission)
        author_formset = SubmissionAuthorFormSet(request.POST, instance=submission, prefix="authors")
        file_formset = SubmissionFileFormSet(request.POST, request.FILES, instance=submission, prefix="files")

        if form.is_valid() and author_formset.is_valid() and file_formset.is_valid():
            submission = form.save()
            author_formset.instance = submission
            author_formset.save()
            file_formset.instance = submission
            file_formset.save()
            messages.success(request, "Draft updated successfully.")
            return redirect("submissions:submission_success")
    else:
        form = SubmissionForm(instance=submission)
        author_formset = SubmissionAuthorFormSet(instance=submission, prefix="authors")
        file_formset = SubmissionFileFormSet(instance=submission, prefix="files")

    return render(
        request,
        "submissions/submission_form.html",
        {
            "form": form,
            "author_formset": author_formset,
            "file_formset": file_formset,
            "submission": submission,
            "mode": "edit",
        },
    )


@login_required
def submission_detail(request, pk):
    researcher = _get_researcher_profile(request.user)
    submission = get_object_or_404(Submission.objects.prefetch_related("authors", "files"), pk=pk)

    if not researcher or not _submission_belongs_to_user(submission, request.user):
        raise PermissionDenied("You do not have permission to view this submission.")

    return render(
        request,
        "submissions/submission_detail.html",
        {
            "submission": submission,
            "researcher": researcher,
        },
    )


@login_required
def submission_success(request):
    return render(request, "submissions/submission_success.html")

