from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer
from apps.common import is_admin
from apps.compute.models import VirtualMachine
from apps.compute.serializers import VmCreateSerializer, VmSerializer
from apps.compute.services import VmLifecycleService, VmProvisioningService


def vm_visible_queryset(user):
    qs = VirtualMachine.objects.select_related("customer", "package")
    if is_admin(user):
        return qs
    return qs.filter(customer=user.customer)


class VmViewSet(viewsets.ModelViewSet):
    serializer_class = VmSerializer
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return vm_visible_queryset(self.request.user)

    def get_serializer_class(self):
        return VmCreateSerializer if self.action == "create" else VmSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vm = VmProvisioningService().request_vm(
            customer=request.user.customer,
            package=serializer.validated_data["package"],
            name=serializer.validated_data["name"],
        )
        return Response(VmSerializer(vm).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        vm = self.get_object()
        VmLifecycleService().delete(vm=vm, actor_customer=None if is_admin(request.user) else request.user.customer)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        vm = self.get_object()
        vm = VmLifecycleService().start(vm=vm, actor_customer=None if is_admin(request.user) else request.user.customer)
        return Response(VmSerializer(vm).data)

    @action(detail=True, methods=["post"])
    def stop(self, request, pk=None):
        vm = self.get_object()
        vm = VmLifecycleService().stop(vm=vm, actor_customer=None if is_admin(request.user) else request.user.customer)
        return Response(VmSerializer(vm).data)


class VmAuditTrailView(generics.ListAPIView):
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        vm = get_object_or_404(vm_visible_queryset(self.request.user), pk=self.kwargs["pk"])
        qs = AuditLog.objects.select_related("customer").filter(entity_type="vm", entity_id=str(vm.id))
        if not is_admin(self.request.user):
            qs = qs.filter(customer=self.request.user.customer)
        return qs
