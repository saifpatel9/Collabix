from django.http import HttpResponse
from django.shortcuts import render


def dashboard_home(request):
    return render(request, "landing/index.html")


def contact(request):
    if request.method != "POST":
        return HttpResponse(status=405)

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
          Message sent successfully!
        </div>
        """
    )
