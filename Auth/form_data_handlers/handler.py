from Auth.form_data_handlers.get_captcha_data import get_captcha_data
from Auth.form_data_handlers.is_allow_access import is_allow_access
from Auth.form_data_handlers.is_an_need_auth import is_an_need_auth
from Auth.form_data_handlers.is_an_need_captcha_key import is_an_need_captcha_key
from Auth.form_data_handlers.is_an_need_two_fact_auth import is_an_need_two_fact_auth


def handler(ctx, params, key):
    if is_an_need_auth(params):
        return ctx.password if key == 'pass' else ctx.data[key]
    if is_an_need_captcha_key(params):
        return get_captcha_data(ctx, params)
    if is_an_need_two_fact_auth(params):
        return input('Enter security code for two-factor authentication: ')
    if is_allow_access(ctx, params):
        ctx.is_allow = True
        return {}
