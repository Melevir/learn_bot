import logging

from learn_bot.enums import Gender

logger = logging.getLogger(__name__)


def guess_gender(first_name: str, last_name: str, default_gender: Gender = Gender.MALE) -> Gender:
    names_info = [
        (
            Gender.MALE,
            {
                "Александр",
                "Алексей",
                "Анатолий",
                "Андрей",
                "Антон",
                "Артем",
                "Валерий",
                "Виктор",
                "Владимир",
                "Владислав",
                "Геннадий",
                "Георгий",
                "Глеб",
                "Денис",
                "Дмитрий",
                "Евгений",
                "Егор",
                "Иван",
                "Игорь",
                "Илья",
                "Иннокентий",
                "Иосиф",
                "Кирилл",
                "Константин",
                "Максим",
                "Марк",
                "Михаил",
                "Муслим",
                "Никита",
                "Николай",
                "Олег",
                "Павел",
                "Риназ",
                "Роман",
                "Ростислав",
                "Семен",
                "Сергей",
                "Собир",
                "Станислав",
                "Стас",
                "Тим",
                "Филипп",
                "Юрий",
            },
        ),
        (
            Gender.FEMALE,
            {
                "Алиса",
                "Анастасия",
                "Ангелина",
                "Ася",
                "Виктория",
                "Дана",
                "Дарья",
                "Диана",
                "Екатерина",
                "Елена",
                "Ксения",
                "Лолита",
                "Мария",
                "Надежда",
                "Ольга",
                "София",
                "Юлдуз",
                "Юлия",
                "Яна",
            },
        ),
    ]
    for possible_gender, gender_names in names_info:
        if first_name.capitalize() in gender_names:
            return possible_gender
    logger.info(f"Cant detect gender for name {first_name}")
    return default_gender
