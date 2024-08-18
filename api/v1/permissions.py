from rest_framework.permissions import BasePermission, SAFE_METHODS
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from product.courses.models import Course, Group
from product.users.models import Subscription, Balance

def make_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            course_id = data.get('course_id')

            user = get_object_or_404(User, id=user_id)
            course = get_object_or_404(Course, id=course_id)
            user_balance = get_object_or_404(Balance, user=user)

            # Проверка баланса
            if user_balance.balance < course.price:
                return JsonResponse({'status': 'error', 'message': 'Insufficient balance.'}, status=400)

            # Списание бонусов
            user_balance.balance -= course.price
            user_balance.save()

            # Открытие доступа к курсу
            user_subscription, created = Subscription.objects.get_or_create(
                user=user,
                course=course,
                defaults={'status': 'active'}
            )
            if not created:
                user_subscription.status = 'active'
                user_subscription.save()

            # Распределение по группам
            groups = list(course.groups.all())
            if groups:
                group = min(groups, key=lambda g: g.students.count())
                group.students.add(user)

            return JsonResponse({'status': 'success', 'message': 'Payment successful'}, status=200)

        except (KeyError, ValueError) as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


class IsStudentOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        # Разрешаем доступ для аутентифицированных пользователей и администраторов
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return True

        # Проверяем, что пользователь - студент
        return hasattr(request.user, 'student')  # Предполагаем, что у студента есть связь с моделью Student

    def has_object_permission(self, request, view, obj):
        # Администраторы имеют доступ ко всем объектам
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Проверяем доступ студента к объекту
        return hasattr(request.user, 'student') and obj.user == request.user


class ReadOnlyOrIsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.method in SAFE_METHODS
