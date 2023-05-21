import dataclasses
import os


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class BotConfig:
    telegram_token: str

    sentry_dsn: str | None

    db_dsn: str
    db_echo: bool

    restart_on_change: bool

    airtable_api_token: str | None
    airtable_database_id: str | None
    airtable_course_table_id: str | None
    airtable_students_table_id: str | None
    airtable_groups_table_id: str | None
    airtable_curators_table_id: str | None


def get_config() -> BotConfig:
    return BotConfig(
        telegram_token=os.environ["TELEGRAM_BOT_TOKEN"],
        sentry_dsn=os.environ.get("SENTRY_DSN"),
        db_dsn=os.environ["DATABASE_DSN"],
        db_echo="DATABASE_ECHO" in os.environ,
        restart_on_change="RESTART_ON_CHANGE" in os.environ,
        airtable_api_token=os.environ.get("AIRTABLE_API_TOKEN"),
        airtable_database_id=os.environ.get("AIRTABLE_DATABASE_ID"),
        airtable_course_table_id=os.environ.get("AIRTABLE_COURSE_TABLE_ID"),
        airtable_students_table_id=os.environ.get("AIRTABLE_STUDENTS_TABLE_ID"),
        airtable_groups_table_id=os.environ.get("AIRTABLE_GROUPS_TABLE_ID"),
        airtable_curators_table_id=os.environ.get("AIRTABLE_CURATORS_TABLE_ID"),
    )
