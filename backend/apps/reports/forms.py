from django import forms

from apps.reports.models import ReportConfig, ReportDashboard


class ReportConfigForm(forms.ModelForm):
    class Meta:
        model = ReportConfig
        fields = [
            "name", "report_type", "description", "filters",
            "is_scheduled", "frequency", "export_format", "recipients",
        ]
        widgets = {
            "filters": forms.Textarea(attrs={"rows": 4, "class": "form-control", "placeholder": '{"key": "value"}'}),
            "recipients": forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": '["email1@example.com"]'}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def clean_filters(self):
        data = self.cleaned_data["filters"]
        if isinstance(data, str):
            import json
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format for filters.")
        return data

    def clean_recipients(self):
        data = self.cleaned_data["recipients"]
        if isinstance(data, str):
            import json
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format for recipients.")
        return data


class ReportDashboardForm(forms.ModelForm):
    class Meta:
        model = ReportDashboard
        fields = ["name", "layout", "widgets", "is_default"]
        widgets = {
            "layout": forms.HiddenInput(),
            "widgets": forms.HiddenInput(),
        }


class ReportFilterForm(forms.Form):
    """Used for filtering analytics views."""
    department = forms.ChoiceField(required=False)
    project = forms.ChoiceField(required=False)
    employee = forms.ChoiceField(required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.employees.models import Department
        from apps.projects.models import Project
        from apps.employees.models import EmployeeProfile

        depts = Department.objects.filter(is_active=True)
        self.fields["department"].choices = [("", "All Departments")] + [(str(d.id), d.name) for d in depts]

        projects = Project.objects.all()
        self.fields["project"].choices = [("", "All Projects")] + [(str(p.id), p.name) for p in projects]

        employees = EmployeeProfile.objects.filter(user__is_active=True)
        self.fields["employee"].choices = [("", "All Employees")] + [(str(e.id), str(e)) for e in employees]
