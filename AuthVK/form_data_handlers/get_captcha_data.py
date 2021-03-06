def get_captcha_data(ctx: any, params: dict) -> str:
    """
    Функция формирует ссылку на страницу капчи, и запрашивает код у пользователя.

    """
    captcha_sid = params.get('captcha_sid')
    captcha_key = input(f'Enter captcha_key[{ctx.main_url}/captcha.php?sid={captcha_sid}]: ')
    if captcha_sid and captcha_key:
        return captcha_key
