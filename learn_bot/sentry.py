import sentry_sdk


def configure_sentry(sentry_dsn: str) -> None:
    sentry_sdk.init(dsn=sentry_dsn)
