def get_captcha_data(ctx: any, params: dict) -> str:
    captcha_sid = params.get('captcha_sid')
    captcha_key = input(f'Enter captcha_key[{ctx.main_uri}/captcha.php?sid={captcha_sid}]: ')
    if captcha_sid and captcha_key:
        return captcha_key
