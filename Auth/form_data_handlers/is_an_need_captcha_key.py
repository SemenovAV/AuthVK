def is_an_need_captcha_key(params: dict) -> bool:
    return 'captcha_key' in params and 'captcha_sid' in params
