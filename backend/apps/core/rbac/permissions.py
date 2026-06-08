from apps.accounts.models import User


ADMIN_ONLY_ROLES: tuple[str, ...] = (User.Role.ADMIN,)
ADMIN_ROLES: tuple[str, ...] = (
    User.Role.ADMIN,
    User.Role.DEPARTMENT_ADMIN,
    User.Role.HR_MANAGER,
)
MANAGER_ROLES: tuple[str, ...] = (User.Role.PROJECT_MANAGER, User.Role.MANAGER)

ROLE_MANAGER_REQUIRED: tuple[str, ...] = (
    User.Role.ADMIN,
    User.Role.DEPARTMENT_ADMIN,
    User.Role.HR_MANAGER,
    User.Role.PROJECT_MANAGER,
    User.Role.MANAGER,
)
ROLE_HR_MANAGER_REQUIRED: tuple[str, ...] = (User.Role.ADMIN, User.Role.HR_MANAGER)
ROLE_DEPARTMENT_ADMIN_REQUIRED: tuple[str, ...] = (
    User.Role.ADMIN,
    User.Role.DEPARTMENT_ADMIN,
    User.Role.HR_MANAGER,
)
ROLE_PROJECT_MANAGER_REQUIRED: tuple[str, ...] = (User.Role.ADMIN, User.Role.PROJECT_MANAGER)
ROLE_EMPLOYEE_REQUIRED: tuple[str, ...] = (
    User.Role.ADMIN,
    User.Role.DEPARTMENT_ADMIN,
    User.Role.HR_MANAGER,
    User.Role.PROJECT_MANAGER,
    User.Role.MANAGER,
    User.Role.EMPLOYEE,
)

ROLE_EMPLOYEE_LIST_ACCESS: tuple[str, ...] = (
    User.Role.ADMIN,
    User.Role.HR_MANAGER,
    User.Role.DEPARTMENT_ADMIN,
    User.Role.MANAGER,
)


def is_authenticated(user) -> bool:
    return bool(getattr(user, "is_authenticated", False))


def is_superuser(user) -> bool:
    return is_authenticated(user) and bool(getattr(user, "is_superuser", False))


def user_has_role(user, roles: tuple[str, ...]) -> bool:
    if not is_authenticated(user):
        return False
    return is_superuser(user) or getattr(user, "role", None) in roles


def is_admin(user) -> bool:
    return user_has_role(user, ADMIN_ROLES)


def is_department_admin(user) -> bool:
    return user_has_role(user, (User.Role.DEPARTMENT_ADMIN,))


def is_hr_manager(user) -> bool:
    return user_has_role(user, (User.Role.HR_MANAGER,))


def is_project_manager(user) -> bool:
    return user_has_role(user, (User.Role.PROJECT_MANAGER,))


def is_manager(user) -> bool:
    return user_has_role(user, MANAGER_ROLES)


def is_employee(user) -> bool:
    if not is_authenticated(user):
        return False
    if is_superuser(user):
        return False
    return getattr(user, "role", None) == User.Role.EMPLOYEE
