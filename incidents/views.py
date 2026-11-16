from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import AlertReviewForm, SOSReportForm
from .models import AlertReview, Notification, SOSReport


def student_reports(user):
    if user.is_staff:
        raise PermissionDenied
    return SOSReport.objects.filter(reporter=user)


@login_required
def report_list(request):
    return render(request, "incidents/list.html", {"reports": student_reports(request.user)})


@login_required
def report_detail(request, pk):
    report = get_object_or_404(student_reports(request.user), pk=pk)
    return render(request, "incidents/detail.html", {"report": report})


@login_required
@require_http_methods(["GET", "POST"])
def report_create(request):
    student_reports(request.user)
    form = SOSReportForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        report = form.save(commit=False)
        report.reporter = request.user
        report.save()
        messages.success(request, "SOS report submitted.")
        return redirect("incidents:detail", pk=report.pk)
    return render(request, "incidents/form.html", {"form": form, "title": "Submit an SOS report"})


@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def report_edit(request, pk):
    reports = student_reports(request.user)
    if request.method == "POST":
        reports = reports.select_for_update()
    report = get_object_or_404(reports, pk=pk)
    if report.status != SOSReport.Status.UNVERIFIED:
        messages.error(request, "Reviewed reports can no longer be edited.")
        return redirect("incidents:detail", pk=report.pk)
    form = SOSReportForm(request.POST if request.method == "POST" else None, instance=report)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "SOS report updated.")
        return redirect("incidents:detail", pk=report.pk)
    return render(request, "incidents/form.html", {"form": form, "title": "Edit SOS report"})


@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def report_delete(request, pk):
    reports = student_reports(request.user)
    if request.method == "POST":
        reports = reports.select_for_update()
    report = get_object_or_404(reports, pk=pk)
    if report.status != SOSReport.Status.UNVERIFIED:
        messages.error(request, "Reviewed reports can no longer be deleted.")
        return redirect("incidents:detail", pk=report.pk)
    if request.method == "POST":
        report.delete()
        messages.success(request, "SOS report deleted.")
        return redirect("incidents:list")
    return render(request, "incidents/delete.html", {"report": report})


@login_required
def review_list(request):
    if not request.user.is_staff:
        raise PermissionDenied
    reports = SOSReport.objects.select_related("reporter")
    return render(request, "incidents/review_list.html", {"reports": reports})


@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def review_detail(request, pk):
    if not request.user.is_staff:
        raise PermissionDenied

    reports = SOSReport.objects.select_related("reporter")
    if request.method == "POST":
        reports = reports.select_for_update(of=("self",))
    report = get_object_or_404(reports, pk=pk)

    form = None
    if report.status == SOSReport.Status.UNVERIFIED:
        form = AlertReviewForm(request.POST if request.method == "POST" else None)
        if request.method == "POST" and form.is_valid():
            review = form.save(commit=False)
            review.report = report
            review.reviewer = request.user
            review.save()
            report.status = review.decision
            report.save(update_fields=["status"])
            if review.decision == AlertReview.Decision.CONFIRMED:
                Notification.objects.create(
                    report=report,
                    title=f"Confirmed campus incident #{report.pk}",
                    message=f"{report.get_category_display()} at {report.location}.",
                )
            messages.success(request, f"SOS report {report.get_status_display().lower()}.")
            return redirect("incidents:review_detail", pk=report.pk)
    elif request.method == "POST":
        messages.error(request, "This SOS report has already been reviewed.")
        return redirect("incidents:review_detail", pk=report.pk)

    return render(request, "incidents/review_detail.html", {"report": report, "form": form})
