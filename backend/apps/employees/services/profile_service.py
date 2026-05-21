from .employee_service import EmployeeService


class EmployeeProfileService:
    visible_to = staticmethod(EmployeeService.visible_to)
    update_status = staticmethod(EmployeeService.update_status)
