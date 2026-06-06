from apps.accounts.models import User


def is_admin(user):
    if not user.is_authenticated:
        return False
    return user.role in (
        User.Role.ADMIN,
        User.Role.DEPARTMENT_ADMIN,
        User.Role.HR_MANAGER,
    )


def is_manager(user):
    if not user.is_authenticated:
        return False
    return user.role in (
        User.Role.PROJECT_MANAGER,
        User.Role.MANAGER,
    )


def is_employee(user):
    if not user.is_authenticated:
        return False
    return user.role == User.Role.EMPLOYEE
