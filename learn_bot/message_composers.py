from learn_bot.bot import Bot
from learn_bot.screenplay.db.models.user import User


def compose_available_commands_message(user: User, bot: Bot) -> str:
    with bot.get_session() as session:
        role = bot.role_provider(user, session)
    allowed_plays = [p for p in bot.screenplay_director.fetch_plays_for_role(role) if p.command_to_start]
    if not allowed_plays:
        return "Кажется, мы с вами не знакомы."
    allowed_commands_lines = "\n".join([
        f"- /{p.command_to_start} – {p.short_description}"
        for p in allowed_plays
    ])
    return f"Доступные команды:\n{allowed_commands_lines}"
