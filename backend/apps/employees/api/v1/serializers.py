from rest_framework import serializers

from apps.accounts.models import User
from apps.employees.models import Department, EmployeeProfile


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "role", "phone", "profile_image",
        ]


class DepartmentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]


class EmployeeListSerializer(serializers.ModelSerializer):
    user = UserReadSerializer(read_only=True)
    department = DepartmentReadSerializer(read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            "id", "employee_id", "designation", "employment_status",
            "joining_date", "user", "department",
        ]


class EmployeeReadSerializer(serializers.ModelSerializer):
    user = UserReadSerializer(read_only=True)
    department = DepartmentReadSerializer(read_only=True)
    manager = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeProfile
        fields = [
            "id", "employee_id", "designation", "employment_status",
            "joining_date", "bio",
            "user", "department", "manager",
            "created_at", "updated_at",
        ]

    def get_manager(self, obj):
        if obj.manager_id:
            return {
                "id": str(obj.manager.id),
                "full_name": obj.manager.user.full_name,
                "employee_id": obj.manager.employee_id,
            }
        return None


class EmployeeCreateSerializer(serializers.Serializer):
    user_full_name = serializers.CharField(max_length=255)
    user_email = serializers.EmailField()
    user_role = serializers.ChoiceField(choices=User.Role.choices)
    user_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    employee_id = serializers.CharField(max_length=50)
    designation = serializers.CharField(max_length=150)
    department = serializers.UUIDField(required=False, allow_null=True)
    manager = serializers.UUIDField(required=False, allow_null=True)
    joining_date = serializers.DateField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True)


class EmployeeUpdateSerializer(serializers.Serializer):
    user_full_name = serializers.CharField(max_length=255, required=False)
    user_email = serializers.EmailField(required=False)
    user_role = serializers.ChoiceField(choices=User.Role.choices, required=False)
    user_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    employee_id = serializers.CharField(max_length=50, required=False)
    designation = serializers.CharField(max_length=150, required=False)
    department = serializers.UUIDField(required=False, allow_null=True)
    manager = serializers.UUIDField(required=False, allow_null=True)
    joining_date = serializers.DateField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True)


class EmployeeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=EmployeeProfile.EmploymentStatus.choices)
