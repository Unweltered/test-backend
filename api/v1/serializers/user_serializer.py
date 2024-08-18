from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from product.users.models import Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    class Meta:
        model = User


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    user = serializers.StringRelatedField()  # Отображает имя пользователя
    course = serializers.StringRelatedField()  # Отображает название курса

    class Meta:
        model = Subscription
        fields = (
            'id',               # Идентификатор подписки
            'user',             # Пользователь, который подписан на курс
            'course',           # Курс, на который оформлена подписка
            'subscribed_at',    # Дата подписки
        )
