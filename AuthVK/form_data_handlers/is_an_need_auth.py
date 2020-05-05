def is_an_need_auth(params: dict) -> bool:
    """
    Функция определяет нужна ли аунтефикация.

    """
    return 'email' in params and 'pass' in params
