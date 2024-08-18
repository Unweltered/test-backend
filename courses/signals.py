from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from product.users.models import Subscription


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """
    Распределение нового студента в группу курса.

    """
    if created:
        course = instance.course
        user = instance.user

        # Получаем все группы курса
        groups = list(course.groups.all())

        # Если групп больше 10, выбираем только первые 10
        if len(groups) > 10:
            groups = groups[:10]

        if groups:
            # Находим группу с наименьшим количеством студентов
            group = min(groups, key=lambda g: g.students.count())

            # Добавляем студента в выбранную группу
            group.students.add(user)
