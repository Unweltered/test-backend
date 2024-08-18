from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    """Кастомная модель пользователя - студента."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=250,
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.get_full_name()


class Balance(models.Model):
    """Модель баланса пользователя."""

    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='balance',
        verbose_name='Пользователь'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000,
        verbose_name='Баланс'
    )

    class Meta:
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'
        ordering = ('-id',)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.amount} бонусов"

    def add_bonus(self, amount):
        """Добавление бонусов."""
        if amount <= 0:
            raise ValidationError("Сумма бонусов должна быть положительной")
        self.amount += amount
        self.save()

    def deduct_bonus(self, amount):
        """Списание бонусов."""
        if self.amount - amount < 0:
            raise ValidationError("Недостаточно бонусов")
        self.amount -= amount
        self.save()

    def save(self, *args, **kwargs):
        if self.amount < 0:
            raise ValidationError("Баланс не может быть ниже 0")
        super().save(*args, **kwargs)


class Subscription(models.Model):
    """Модель подписки пользователя на курс."""

    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='subscribed_users',
        verbose_name='Курс'
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-subscribed_at',)
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.get_full_name()} подписан на {self.course.title}"


class UserProduct(models.Model):
    """Модель для отслеживания доступа пользователя к продукту."""

    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='accessed_products',
        verbose_name='Пользователь'
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='accessed_by_users',
        verbose_name='Курс'
    )
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата приобретения')

    class Meta:
        verbose_name = 'Доступ к продукту'
        verbose_name_plural = 'Доступы к продуктам'
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.course.title}"
