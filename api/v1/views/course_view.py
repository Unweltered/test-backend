from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from product.api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin
from product.api.v1.serializers.course_serializer import (CourseSerializer,
                                                          CreateCourseSerializer,
                                                          CreateGroupSerializer,
                                                          CreateLessonSerializer,
                                                          GroupSerializer,
                                                          LessonSerializer)
from product.api.v1.serializers.user_serializer import SubscriptionSerializer
from product.courses.models import Course
from product.users.models import Subscription, Balance


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """

    queryset = Course.objects.all()
    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk=None):
        """Покупка доступа к курсу (подписка на курс)."""

        course = get_object_or_404(Course, pk=pk)
        user = request.user

        # Проверка наличия UserBalance
        user_balance = get_object_or_404(Balance, user=user)
        if user_balance.balance < course.price:
            return Response(
                {'detail': 'Insufficient balance.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Списание бонусов
        user_balance.balance -= course.price
        user_balance.save()

        # Создание или обновление подписки на курс
        user_subscription, created = Subscription.objects.get_or_create(
            user=user,
            course=course,
            defaults={'status': 'active'}
        )
        if not created:
            user_subscription.status = 'active'
            user_subscription.save()

        return Response(
            {'status': 'Payment successful'},
            status=status.HTTP_200_OK
        )
