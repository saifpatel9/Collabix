from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.core.forms import ContactForm
from apps.core.selectors.dashboard_selectors import DashboardSelector
from apps.employees.models import EmployeeProfile
from apps.projects.models import Project
from apps.tasks.models import Task


def landing_home(request):
    return render(request, "landing/index.html")


@login_required
def dashboard_home(request):
    context = get_dashboard_context(request.user)
    template_name = "dashboard/home.html"
    if request.headers.get("HX-Request") == "true":
        section = request.GET.get("section", "stats")
        if section == "employees":
            template_name = "dashboard/partials/employee_table.html"
            page = request.GET.get("page", 1)
            employees = EmployeeProfile.objects.select_related("user", "department", "manager__user").order_by("-created_at")
            paginator = Paginator(employees, request.GET.get("page_size", 10))
            context["employees"] = paginator.get_page(page)
        elif section == "tasks":
            template_name = "dashboard/partials/task_table.html"
            page = request.GET.get("page", 1)
            tasks = Task.objects.select_related("project", "created_by__user").prefetch_related("assignments__employee__user").filter(is_archived=False).order_by("-created_at")
            paginator = Paginator(tasks, request.GET.get("page_size", 10))
            context["tasks"] = paginator.get_page(page)
        else:
            template_name = "dashboard/partials/widgets.html"
    return render(request, template_name, context)


def get_dashboard_context(user=None):
    ctx = DashboardSelector.metrics_for(user)
    from django.utils import timezone
    ctx["today"] = timezone.localdate()
    ctx["now"] = timezone.localtime()
    ctx["recent_projects"] = Project.objects.filter(is_archived=False).select_related("owner__user", "department").order_by("-created_at")[:5]
    visible_tasks = Task.objects.filter(is_archived=False)
    if user and user.is_authenticated and not user.is_superuser:
        from apps.tasks.selectors.task_selectors import TaskSelector
        visible_tasks = TaskSelector.active_for(user)
    tasks_qs = visible_tasks.select_related("project", "created_by__user").prefetch_related("assignments__employee__user").order_by("-created_at")
    paginator = Paginator(tasks_qs, 10)
    ctx["tasks"] = paginator.get_page(1)
    return ctx


def contact(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponse(
            """
            <div style="
              display: flex; align-items: center; gap: 10px;
              background: rgba(16,185,129,0.12);
              border: 1px solid rgba(16,185,129,0.3);
              border-radius: 10px; padding: 14px 18px;
              color: #6ee7b7; font-size: 0.9rem; font-weight: 500;
              margin-top: 8px;
            ">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Thank you! Your message has been sent. Our team will respond within 1 business day.
            </div>
            """
        )

    errors = "".join(
        f'<li style="margin-bottom:4px">{", ".join(v)}</li>'
        for v in form.errors.values()
    )
    return HttpResponse(
        f"""
        <div style="
          background: rgba(239,68,68,0.12);
          border: 1px solid rgba(239,68,68,0.3);
          border-radius: 10px; padding: 14px 18px;
          color: #fca5a5; font-size: 0.9rem; font-weight: 500;
          margin-top: 8px;
        ">
          <p style="margin-bottom:6px;font-weight:600">Please fix the following errors:</p>
          <ul style="margin:0;padding-left:18px">{errors}</ul>
        </div>
        """
    )
