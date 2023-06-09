import dataclasses
import os


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class BotConfig:
    telegram_token: str

    db_dsn: str
    db_echo: bool = False

    restart_on_change: bool = False

    sentry_dsn: str | None = None

    airtable_api_token: str | None = None
    airtable_database_id: str | None = None
    airtable_course_table_id: str | None = None
    airtable_students_table_id: str | None = None
    airtable_groups_table_id: str | None = None
    airtable_curators_table_id: str | None = None


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
