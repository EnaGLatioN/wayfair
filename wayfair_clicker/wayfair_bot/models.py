from uuid import uuid4

from django.db.models import (
    Model,
    PositiveIntegerField,
    UUIDField,
    DateTimeField,
    TextField,
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
    created_at = DateTimeField(
        auto_now_add=True,
        help_text="Дата создания",
        verbose_name="Дата создания",
    )
    token = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    X_PX_OS_VERSION = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    Accept_Language = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default='ru'
    )
    X_PX_VID = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    Connection = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default='keep-alive'
    )
    Accept = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default='application/json'
    )
    X_PX_DEVICE_FP =  TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    wf_customer_guid =  TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    X_PX_HELLO =  TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    wf_pageview_id = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    X_PX_MOBILE_SDK_VERSION = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    X_Graph_Type = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    Content_Type = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default='application/json'
    )
    X_PX_AUTHORIZATION = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    User_Agent = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    wf_locale = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default='en-US'
    )
    X_PX_UUID = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    AppAuthEnabled = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    Accept_Encoding = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default='gzip, deflate, br'
    )
    X_PX_DEVICE_MODEL = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    wf_device_guid = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    Host = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default='www.wayfair.com'
    )
    Cookie = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default=None
    )
    X_PX_OS = TextField(
        help_text="Токен вэйфэир",
        blank=True,
        null=True,
        default='iOS'
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


class Order(Model):
    id = UUIDField(
        default=uuid4,
        help_text="Уникальный идентификатор ",
        primary_key=True,
        verbose_name="ID",
    )
    order_id = BigIntegerField(
        blank=True,
        null=True,
        help_text="Уникальный идентификатор TG",
        default=0
    )