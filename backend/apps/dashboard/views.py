from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.core.selectors.dashboard_selectors import DashboardSelector


def landing_home(request):
    return render(request, "landing/index.html")


@login_required
def dashboard_home(request):
    context = get_dashboard_context(request.user)
    template_name = (
        "dashboard/partials/widgets.html"
        if request.headers.get("HX-Request") == "true"
        else "dashboard/home.html"
    )
    return render(request, template_name, context)


def get_dashboard_context(user=None):
    return DashboardSelector.metrics_for(user)


def contact(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    return HttpResponse("""
        <div style="
          display: flex; align-items: center; gap: 10px;
          background: rgba(16,185,129,0.12);
          border: 1px solid rgba(16,185,129,0.3);
          border-radius: 10px; padding: 14px 18px;
          color: #6ee7b7; font-size: 0.9rem; font-weight: 500;
          margin-top: 8px;
        ">
          Message sent successfully!
        </div>
        """)
