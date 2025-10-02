from uuid import uuid4

from django.db.models import (
    Model,
    PositiveIntegerField,
    UUIDField,
    DateTimeField,
    TextField,
    ForeignKey,
    CASCADE,
    BooleanField,
    BigIntegerField,
    OneToOneField
)


class Token(Model):
    id = UUIDField(
        default=uuid4,
        help_text="Уникальный идентификатор ",
        primary_key=True,
        verbose_name="ID",
    )
    token = TextField(
        help_text="Токен вэйфэир"
    )
    created_at = DateTimeField(
        auto_now_add=True,
        help_text="Дата создания",
        verbose_name="Дата создания",
    )

    class Meta:
        db_table = "token"
        verbose_name = "token"
        verbose_name_plural = "token"
        ordering = ["-created_at"]


class Process(Model):
    id = UUIDField(
        default=uuid4,
        help_text="Уникальный идентификатор ",
        primary_key=True,
        verbose_name="ID",
    )
    pid = PositiveIntegerField(
        help_text="Айди процесса",
        verbose_name="Айди процесса"
    )
    created_at = DateTimeField(
        auto_now_add=True,
        help_text="Дата создания",
        verbose_name="Дата создания",
    )
    status = BooleanField(
        help_text="Активность",
        default=True
    )

    class Meta:
        db_table = "process"
        verbose_name = "Процесс"
        verbose_name_plural = "Процесс"
        ordering = ["-created_at"]


class User(Model):
    id = UUIDField(
        default=uuid4,
        help_text="Уникальный идентификатор ",
        primary_key=True,
        verbose_name="ID",
    )
    telegram_id = BigIntegerField(
        blank=True,
        null=True,
        help_text="Уникальный идентификатор TG",
    )
    created_at = DateTimeField(
        auto_now_add=True,
        help_text="Дата создания",
        verbose_name="Дата создания",
    )
    tg_token = OneToOneField(
        Token,
        on_delete=CASCADE,
        related_name='telegram_user',
        help_text="Токен пользователя",
        verbose_name="Токен",
        null=True,
        blank=True
    )
    process = OneToOneField(
        Process,
        on_delete=CASCADE,
        related_name='user_for_process',
        help_text="Токен пользователя",
        verbose_name="Токен",
        null=True,
        blank=True
    )

    class Meta:
        db_table = "user"
        verbose_name = "user"
        verbose_name_plural = "user"
        ordering = ["-created_at"]
