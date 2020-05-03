def is_an_need_two_fact_auth(params: dict) -> bool:
    """
    Функция определяет запрос кода(второй фактор)

    """
    return 'code' in params
