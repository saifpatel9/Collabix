from apps.core.rbac.permissions import (
    can_manage_employees,
    can_view_employee_directory,
    is_admin,
    is_employee,
    is_manager,
)

from apps.core.rbac.policies import (
    can_create_project,
    can_create_team,
    can_view_admin_dashboard,
    can_view_all_activity,
    can_view_people,
)


def rbac_context(request):
    if not request.user.is_authenticated:
        return {
            "is_admin": False,
            "is_manager": False,
            "is_employee": False,
            "can_view_admin_dashboard": False,
            "can_view_people": False,
            "can_view_employees": False,
            "can_manage_people": False,
            "can_create_project": False,
            "can_create_team": False,
            "can_view_all_activity": False,
            "APP_NAME": "Collabix",
            "COMPANY_NAME": "Collabix Internal",
        }

    user = request.user

    user_is_admin = is_admin(user)
    user_is_manager = is_manager(user)
    user_is_employee = is_employee(user)

    can_view_employees = can_view_employee_directory(user)
    can_manage_people = can_manage_employees(user)

    return {
        "is_admin": user_is_admin,
        "is_manager": user_is_manager,
        "is_employee": user_is_employee,
        "can_view_admin_dashboard": can_view_admin_dashboard(user),
        "can_view_people": can_view_people(user),
        "can_view_employees": can_view_employees,
        "can_manage_people": can_manage_people,
        "can_create_project": can_create_project(user),
        "can_create_team": can_create_team(user),
        "can_view_all_activity": can_view_all_activity(user),
        "APP_NAME": "Collabix",
        "COMPANY_NAME": "Collabix Internal",
    }