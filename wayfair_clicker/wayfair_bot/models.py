from uuid import uuid4

from django.db.models import (
    Model,
    PositiveIntegerField,
    UUIDField,
    DateTimeField,
    TextField,
    ForeignKey,
    CASCADE,
    BooleanField
)


class Token(Model):
    token = TextField(
        help_text="Токен вэйфэир"
    )


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
    pc_token = ForeignKey(
        Token,
        verbose_name="Создатель",
        on_delete=CASCADE,
        null=True,
        blank=True,
        related_name='tokoken'
    )

    class Meta:
        db_table = "process"
        verbose_name = "Процесс"
        verbose_name_plural = "Процесс"
        ordering = ["-created_at"]

