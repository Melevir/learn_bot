import sqlalchemy as sa


class TimestampsMixin:
    __abstract__ = True

    __created_at_name__ = "created_at"
    __updated_at_name__ = "updated_at"
    __datetime_func__ = sa.func.now()

    created_at = sa.Column(
        __created_at_name__,
        sa.TIMESTAMP(timezone=False),
        default=__datetime_func__,
        server_default=sa.text("now()"),
        nullable=False,
    )

    updated_at = sa.Column(
        __updated_at_name__,
        sa.TIMESTAMP(timezone=False),
        onupdate=__datetime_func__,
        server_default=sa.text("now()"),
        nullable=False,
    )
