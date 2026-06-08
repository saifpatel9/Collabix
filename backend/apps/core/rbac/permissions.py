from apps.accounts.models import User

# =========================================================
# ROLE GROUPS (SOURCE OF TRUTH)
# =========================================================

ADMIN_ROLES = (User.Role.ADMIN,)

ELEVATED_ROLES = (
    User.Role.ADMIN,
    User.Role.DEPARTMENT_ADMIN,
    User.Role.HR_MANAGER,
)

MANAGEMENT_ROLES = (
    User.Role.PROJECT_MANAGER,
    User.Role.MANAGER,
)

ALL_MANAGEMENT_ROLES = (
    User.Role.ADMIN,
    User.Role.DEPARTMENT_ADMIN,
    User.Role.HR_MANAGER,
    User.Role.PROJECT_MANAGER,
    User.Role.MANAGER,
    User.Role.EMPLOYEE,
)

EMPLOYEE_DIRECTORY_ROLES = (
    User.Role.ADMIN,
    User.Role.HR_MANAGER,
    User.Role.DEPARTMENT_ADMIN,
    User.Role.MANAGER,
)

PROJECT_MODULE_ROLES = (
    User.Role.ADMIN,
    User.Role.PROJECT_MANAGER,
)

HR_MODULE_ROLES = (
    User.Role.ADMIN,
    User.Role.HR_MANAGER,
)

DEPARTMENT_MODULE_ROLES = (
    User.Role.ADMIN,
    User.Role.DEPARTMENT_ADMIN,
    User.Role.HR_MANAGER,
)

INTERNAL_ROLES = ALL_MANAGEMENT_ROLES


# =========================================================
# CORE AUTH HELPERS (FIXED)
# =========================================================

def is_authenticated(user) -> bool:
    return bool(user and getattr(user, "is_authenticated", False))


def is_superuser(user) -> bool:
    return is_authenticated(user) and getattr(user, "is_superuser", False)


def has_role(user, roles: tuple[str, ...]) -> bool:
    if not is_authenticated(user):
        return False

    if is_superuser(user):
        return True

    return getattr(user, "role", None) in roles


# =========================================================
# ROLE CHECKERS
# =========================================================

def is_admin(user) -> bool:
    return has_role(user, ADMIN_ROLES)


def is_elevated_user(user) -> bool:
    return has_role(user, ELEVATED_ROLES)


def is_department_admin(user) -> bool:
    return has_role(user, (User.Role.DEPARTMENT_ADMIN,))


def is_hr_manager(user) -> bool:
    return has_role(user, (User.Role.HR_MANAGER,))


def is_project_manager(user) -> bool:
    return has_role(user, (User.Role.PROJECT_MANAGER,))


def is_manager(user) -> bool:
    return has_role(user, MANAGEMENT_ROLES)


def is_management_user(user) -> bool:
    return has_role(user, ALL_MANAGEMENT_ROLES)


def is_employee(user) -> bool:
    return (
        is_authenticated(user)
        and not is_superuser(user)
        and getattr(user, "role", None) == User.Role.EMPLOYEE
    )


# =========================================================
# ACTION PERMISSIONS
# =========================================================

def can_manage_employees(user):
    return has_role(user, DEPARTMENT_MODULE_ROLES)


def can_view_employee_directory(user):
    return has_role(user, EMPLOYEE_DIRECTORY_ROLES)


def can_manage_projects(user):
    return has_role(user, PROJECT_MODULE_ROLES)


def can_manage_tasks(user):
    return has_role(user, (
        User.Role.ADMIN,
        User.Role.PROJECT_MANAGER,
        User.Role.MANAGER,
    ))