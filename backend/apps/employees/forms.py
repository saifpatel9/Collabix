from django import forms

from apps.accounts.models import User

from .models import (
    Department,
    Designation,
    EmployeeHierarchy,
    EmployeeProfile,
    OrganizationPosition,
)

INPUT_CLASS = (
    "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm "
    "text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-4 "
    "focus:ring-cyan-100 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
)


class TailwindFormMixin:
    def _apply_base_classes(self):
        for field in self.fields.values():
            if isinstance(field.widget, (forms.CheckboxInput, forms.FileInput)):
                continue
            current = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{current} {INPUT_CLASS}".strip()


class DepartmentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Department
        fields = ("name", "description", "head", "is_active")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "is_active": forms.CheckboxInput(
                attrs={"class": "h-4 w-4 rounded border-slate-300 text-cyan-600"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["head"].queryset = User.objects.filter(is_active=True).order_by(
            "full_name"
        )
        self._apply_base_classes()


class EmployeeProfileForm(TailwindFormMixin, forms.ModelForm):
    user_full_name = forms.CharField(label="Full name", max_length=255)
    user_email = forms.EmailField(label="Email")
    user_role = forms.ChoiceField(label="Role", choices=User.Role.choices)
    user_phone = forms.CharField(label="Phone", max_length=20, required=False)

    class Meta:
        model = EmployeeProfile
        fields = (
            "employee_id",
            "designation",
            "department",
            "manager",
            "joining_date",
            "employment_status",
            "bio",
        )
        widgets = {
            "joining_date": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = Department.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["manager"].queryset = EmployeeProfile.objects.select_related(
            "user"
        ).order_by("user__full_name")

        if self.instance and self.instance.pk:
            self.fields["manager"].queryset = self.fields["manager"].queryset.exclude(
                pk=self.instance.pk
            )
            if hasattr(self.instance, "user"):
                self.fields["user_full_name"].initial = self.instance.user.full_name
                self.fields["user_email"].initial = self.instance.user.email
                self.fields["user_role"].initial = self.instance.user.role
                self.fields["user_phone"].initial = self.instance.user.phone

        self._apply_base_classes()


class EmployeeStatusForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ("employment_status",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employment_status"].widget.attrs["class"] = INPUT_CLASS


class EmployeeHierarchyForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = EmployeeHierarchy
        fields = ("employee", "reporting_manager", "effective_from")
        widgets = {"effective_from": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = EmployeeProfile.objects.select_related("user").order_by(
            "user__full_name"
        )
        self.fields["employee"].queryset = queryset
        self.fields["reporting_manager"].queryset = queryset
        self._apply_base_classes()


class DesignationForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Designation
        fields = ("title", "level", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_classes()


class OrganizationPositionForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationPosition
        fields = ("employee", "designation", "department", "reporting_position")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].queryset = EmployeeProfile.objects.select_related(
            "user"
        ).order_by("user__full_name")
        self.fields["designation"].queryset = Designation.objects.order_by(
            "level", "title"
        )
        self.fields["department"].queryset = Department.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["reporting_position"].queryset = (
            OrganizationPosition.objects.select_related(
                "employee__user", "designation"
            ).order_by("employee__user__full_name")
        )
        if self.instance and self.instance.pk:
            self.fields["reporting_position"].queryset = self.fields[
                "reporting_position"
            ].queryset.exclude(pk=self.instance.pk)
        self._apply_base_classes()