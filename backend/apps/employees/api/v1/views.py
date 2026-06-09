from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.pagination import StandardResultsSetPagination
from apps.core.api.responses import api_response
from apps.employees.services.employee_service import EmployeeService

from .permissions import CanManageEmployees, CanViewEmployeeDirectory
from .serializers import (
    EmployeeCreateSerializer,
    EmployeeListSerializer,
    EmployeeReadSerializer,
    EmployeeStatusSerializer,
    EmployeeUpdateSerializer,
)


class EmployeeListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), CanViewEmployeeDirectory()]
        return [IsAuthenticated(), CanManageEmployees()]

    def get(self, request):
        queryset = EmployeeService.visible_to(request.user)
        queryset = EmployeeService.search_and_filter(
            queryset,
            search=request.query_params.get("search"),
            department=request.query_params.get("department"),
            manager=request.query_params.get("manager"),
            employment_status=request.query_params.get("employment_status"),
        )
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = EmployeeListSerializer(page, many=True)
            return api_response(
                data={
                    "count": paginator.page.paginator.count,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                    "results": serializer.data,
                }
            )
        serializer = EmployeeListSerializer(queryset, many=True)
        return api_response(data=serializer.data)

    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            employee = EmployeeService.create(
                cleaned_data=serializer.validated_data,
                performed_by=request.user,
            )
        except PermissionDenied as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_403_FORBIDDEN,
            )
        except DjangoValidationError as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return api_response(
            message="Employee created successfully.",
            data=EmployeeReadSerializer(employee).data,
            status_code=status.HTTP_201_CREATED,
        )


class EmployeeDetailUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        employee = get_object_or_404(
            EmployeeService.visible_to(request.user), pk=pk
        )
        serializer = EmployeeReadSerializer(employee)
        return api_response(data=serializer.data)

    def patch(self, request, pk):
        employee = get_object_or_404(
            EmployeeService.visible_to(request.user), pk=pk
        )
        serializer = EmployeeUpdateSerializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        try:
            employee = EmployeeService.update(
                employee=employee,
                cleaned_data=serializer.validated_data,
                performed_by=request.user,
            )
        except PermissionDenied as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_403_FORBIDDEN,
            )
        except DjangoValidationError as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return api_response(
            message="Employee updated successfully.",
            data=EmployeeReadSerializer(employee).data,
        )


class EmployeeStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        employee = get_object_or_404(
            EmployeeService.visible_to(request.user), pk=pk
        )
        serializer = EmployeeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            employee = EmployeeService.update_status(
                employee=employee,
                status=serializer.validated_data["status"],
                performed_by=request.user,
            )
        except PermissionDenied as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_403_FORBIDDEN,
            )
        except DjangoValidationError as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return api_response(
            message="Employee status updated successfully.",
            data=EmployeeReadSerializer(employee).data,
        )


class EmployeeDeactivateView(APIView):
    permission_classes = [IsAuthenticated, CanManageEmployees]

    def post(self, request, pk):
        employee = get_object_or_404(
            EmployeeService.visible_to(request.user), pk=pk
        )
        try:
            employee = EmployeeService.deactivate(
                employee=employee,
                performed_by=request.user,
            )
        except PermissionDenied as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_403_FORBIDDEN,
            )
        except DjangoValidationError as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return api_response(
            message="Employee deactivated successfully.",
            data=EmployeeReadSerializer(employee).data,
        )
