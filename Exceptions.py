class EmptyAnswerFromApi(Exception):
    """Исключение, пустой ответ от АПИ."""

    pass


class NoRequiredVariables(Exception):
    """Исключение, нет нужных переменных."""

    pass

class IncorrectStatusCode(Exception):
    """Исключение, неверный код ответа"""

    pass
