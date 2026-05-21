from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.accounts.models import User
from apps.core.permissions import (
    AdminRequiredMixin,
    EmployeeAccessMixin,
    ManagerRequiredMixin,
)

from .forms import DepartmentForm, EmployeeProfileForm, EmployeeStatusForm
from .models import Department, EmployeeProfile
from .services.department_service import DepartmentService
from .services.employee_service import EmployeeService


def is_htmx(request):
    return request.headers.get("HX-Request") == "true"


class DepartmentListView(ManagerRequiredMixin, ListView):
    model = Department
    template_name = "departments/list.html"
    context_object_name = "departments"
    paginate_by = 10

    def get_queryset(self):
        queryset = DepartmentService.visible_to(self.request.user)
        return DepartmentService.search(queryset, self.request.GET.get("q"))

    def get_template_names(self):
        if is_htmx(self.request):
            return ["departments/partials/table.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        return context


class DepartmentDetailView(ManagerRequiredMixin, DetailView):
    model = Department
    template_name = "departments/detail.html"
    context_object_name = "department"

    def get_queryset(self):
        return DepartmentService.visible_to(self.request.user)


class DepartmentCreateView(AdminRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "departments/form.html"
    success_url = reverse_lazy("employees:department_list")

    def form_valid(self, form):
        DepartmentService.create(cleaned_data=form.cleaned_data)
        messages.success(self.request, "Department created successfully.")
        return redirect(self.success_url)


class DepartmentUpdateView(AdminRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = "departments/form.html"
    success_url = reverse_lazy("employees:department_list")

    def form_valid(self, form):
        DepartmentService.update(department=self.object, cleaned_data=form.cleaned_data)
        messages.success(self.request, "Department updated successfully.")
        return redirect(self.success_url)


class DepartmentDeleteView(AdminRequiredMixin, DeleteView):
    model = Department
    template_name = "departments/confirm_delete.html"
    success_url = reverse_lazy("employees:department_list")

    def form_valid(self, form):
        DepartmentService.delete(department=self.object)
        messages.success(self.request, "Department deleted successfully.")
        return redirect(self.success_url)


class EmployeeListView(LoginRequiredMixin, ListView):
    model = EmployeeProfile
    template_name = "employees/list.html"
    context_object_name = "employees"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if (
            request.user.role not in (User.Role.ADMIN, User.Role.MANAGER)
            and not request.user.is_superuser
        ):
            return redirect("employees:employee_profile")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = EmployeeService.visible_to(self.request.user)
        return EmployeeService.search_and_filter(
            queryset,
            search=self.request.GET.get("q"),
            department=self.request.GET.get("department"),
            manager=self.request.GET.get("manager"),
            employment_status=self.request.GET.get("employment_status"),
        )

    def get_template_names(self):
        if is_htmx(self.request):
            return ["employees/partials/table.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["departments"] = Department.objects.filter(is_active=True).order_by(
            "name"
        )
        context["managers"] = EmployeeProfile.objects.select_related("user").filter(
            user__role__in=[User.Role.ADMIN, User.Role.MANAGER],
            employment_status=EmployeeProfile.EmploymentStatus.ACTIVE,
        )
        context["statuses"] = EmployeeProfile.EmploymentStatus.choices
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "department": self.request.GET.get("department", ""),
            "manager": self.request.GET.get("manager", ""),
            "employment_status": self.request.GET.get("employment_status", ""),
        }
        return context


class EmployeeDetailView(EmployeeAccessMixin, DetailView):
    model = EmployeeProfile
    template_name = "employees/detail.html"
    context_object_name = "employee"

    def get_object(self, queryset=None):
        return self.employee_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = EmployeeProfile.EmploymentStatus.choices
        return context


class EmployeeProfileView(LoginRequiredMixin, DetailView):
    model = EmployeeProfile
    template_name = "employees/profile.html"
    context_object_name = "employee"

    def get_object(self, queryset=None):
        return get_object_or_404(
            EmployeeProfile.objects.select_related(
                "user", "department", "manager__user"
            ),
            user=self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = EmployeeProfile.EmploymentStatus.choices
        return context


class EmployeeCreateView(AdminRequiredMixin, CreateView):
    model = EmployeeProfile
    form_class = EmployeeProfileForm
    template_name = "employees/form.html"
    success_url = reverse_lazy("employees:employee_list")

    def form_valid(self, form):
        EmployeeService.create(cleaned_data=form.cleaned_data)
        messages.success(self.request, "Employee profile created successfully.")
        return redirect(self.success_url)


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = EmployeeProfile
    form_class = EmployeeProfileForm
    template_name = "employees/form.html"
    success_url = reverse_lazy("employees:employee_list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.object = self.get_object()
        if request.user.is_superuser or request.user.role == User.Role.ADMIN:
            return super().dispatch(request, *args, **kwargs)
        if (
            request.user.role == User.Role.MANAGER
            and self.object.manager
            and self.object.manager.user_id == request.user.id
        ):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form):
        EmployeeService.update(employee=self.object, cleaned_data=form.cleaned_data)
        messages.success(self.request, "Employee profile updated successfully.")
        return redirect(self.success_url)


class EmployeeStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = EmployeeProfile
    form_class = EmployeeStatusForm
    template_name = "employees/partials/status_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.object = self.get_object()
        if request.user.is_superuser or request.user.role == User.Role.ADMIN:
            return super().dispatch(request, *args, **kwargs)
        if (
            request.user.role == User.Role.MANAGER
            and self.object.manager
            and self.object.manager.user_id == request.user.id
        ):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form):
        EmployeeService.update_status(
            employee=self.object, status=form.cleaned_data["employment_status"]
        )
        messages.success(self.request, "Employee status updated.")
        if is_htmx(self.request):
            return redirect("employees:employee_detail", pk=self.object.pk)
        return redirect("employees:employee_detail", pk=self.object.pk)
