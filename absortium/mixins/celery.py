__author__ = 'andrew.shvv@gmail.com'

import uuid

from celery.exceptions import TimeoutError
from celery.result import AsyncResult
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_201_CREATED

from core.utils.logging import getPrettyLogger

logger = getPrettyLogger(__name__)


class CreateCeleryMixin():
    @detail_route()
    def check(self, request, *args, **kwargs):

        try:
            task_id = request.data['id']
            uuid.UUID(task_id)
        except KeyError:
            raise ValidationError("You should specify id")
        except ValueError:
            raise ValidationError("Not valid id")

        async_result = AsyncResult(task_id)

        try:
            result = async_result.get(timeout=0.5, propagate=False)
        except TimeoutError:
            result = None
        status = async_result.status

        if isinstance(result, Exception):
            return Response({
                'status': status,
                'error': str(result),
            }, status=HTTP_200_OK)
        elif result is None:
            return Response({
                'status': status
            }, status=HTTP_204_NO_CONTENT)
        else:
            return Response({
                'status': status,
                'result': result,
            }, status=HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        async_result = self.create_in_celery(request, *args, **kwargs)

        try:
            obj = async_result.get(timeout=10, propagate=True)
            return Response(obj, status=HTTP_201_CREATED)
        except TimeoutError:
            data = {
                "id": async_result.id
            }
            return Response(data, status=HTTP_204_NO_CONTENT)

    def create_in_celery(self, request, *args, **kwargs):
        raise NotImplemented("You should implement 'create_in_celery' method")


class ApproveCeleryMixin():
    @detail_route(methods=['post'])
    def approve(self, request, *args, **kwargs):
        async_result = self.approve_in_celery(request, *args, **kwargs)

        try:
            obj = async_result.get(timeout=10, propagate=True)
            return Response(obj, status=HTTP_200_OK)
        except TimeoutError:
            data = {
                "id": async_result.id
            }
            return Response(data, status=HTTP_204_NO_CONTENT)

    def approve_in_celery(self, request, *args, **kwargs):
        raise NotImplemented("You should implement 'approve_in_celery' method")


class UpdateCeleryMixin():
    def update(self, request, *args, **kwargs):
        async_result = self.update_in_celery(request, *args, **kwargs)

        try:
            obj = async_result.get(timeout=10, propagate=True)
            return Response(obj, status=HTTP_200_OK)
        except TimeoutError:
            data = {
                "id": async_result.id
            }
            return Response(data, status=HTTP_204_NO_CONTENT)

    def update_in_celery(self, request, *args, **kwargs):
        raise NotImplemented("You should implement 'approve_in_celery' method")


class DestroyCeleryMixin():
    def destroy(self, request, *args, **kwargs):
        async_result = self.destroy_in_celery(request, *args, **kwargs)

        try:
            obj = async_result.get(timeout=10, propagate=True)
            return Response(obj, status=HTTP_200_OK)
        except TimeoutError:
            data = {
                "id": async_result.id
            }
            return Response(data, status=HTTP_204_NO_CONTENT)

    def destroy_in_celery(self, request, *args, **kwargs):
        raise NotImplemented("You should implement 'destroy_in_celery' method")


class LockCeleryMixin():
    @detail_route(methods=['post'])
    def lock(self, request, *args, **kwargs):
        async_result = self.lock_in_celery(request, *args, **kwargs)

        try:
            obj = async_result.get(timeout=10, propagate=True)
            return Response(obj, status=HTTP_200_OK)
        except TimeoutError:
            data = {
                "id": async_result.id
            }
            return Response(data, status=HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'])
    def unlock(self, request, *args, **kwargs):
        async_result = self.unlock_in_celery(request, *args, **kwargs)

        try:
            obj = async_result.get(timeout=10, propagate=True)
            return Response(obj, status=HTTP_200_OK)
        except TimeoutError:
            data = {
                "id": async_result.id
            }
            return Response(data, status=HTTP_204_NO_CONTENT)

    def lock_in_celery(self, request, *args, **kwargs):
        raise NotImplemented("You should implement 'destroy_in_celery' method")

    def unlock_in_celery(self, request, *args, **kwargs):
        raise NotImplemented("You should implement 'destroy_in_celery' method")
