from apps.core.rbac.utils import is_admin, is_manager, is_employee


def rbac_context(request):
    if not request.user.is_authenticated:
        return {
            "is_admin": False,
            "is_manager": False,
            "is_employee": False,
            "can_view_admin_dashboard": False,
            "can_view_people": False,
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

    return {
        "is_admin": user_is_admin,
        "is_manager": user_is_manager,
        "is_employee": user_is_employee,
        "can_view_admin_dashboard": user_is_admin,
        "can_view_people": user_is_admin,
        "can_create_project": not user_is_employee,
        "can_create_team": not user_is_employee,
        "can_view_all_activity": user_is_admin,
        "APP_NAME": "Collabix",
        "COMPANY_NAME": "Collabix Internal",
    }
