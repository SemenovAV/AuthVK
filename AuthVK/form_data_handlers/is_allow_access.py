def is_allow_access(ctx: any, params: dict) -> bool:
    """
    Функция проверяет прошла ли авторизация.
    """
    return params == {} and ('grant_access' in ctx.response.url or 'access_token' in ctx.response.url)