def is_an_need_auth(params: dict) -> bool:
    return 'email' in params and 'pass' in params
