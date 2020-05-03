from Auth.form_data_handlers.get_captcha_data import get_captcha_data
from Auth.form_data_handlers.is_allow_access import is_allow_access
from Auth.form_data_handlers.is_an_need_auth import is_an_need_auth
from Auth.form_data_handlers.is_an_need_captcha_key import is_an_need_captcha_key
from Auth.form_data_handlers.is_an_need_two_fact_auth import is_an_need_two_fact_auth


def handler(ctx, params, key):
    """
    Вспомогательная функция, вызывается методом Auth.parse_form каждый раз когда
    обрабатывается очередная форма. Должен возвращать то что надо ввести в
    требуемое поле формы. Имя поля приходит третьим параметром(key).
    В данном случае обрабатывает:
       аунтификацию,первый фактор(логин и пароль) - отдает то что передано параметрами в Auth,
        и второй фактор(присылаемый код)  - Выбрасывает в консоль запрос кода.
       капчу, - выбрасывает в консоль запрос кода с ссылкой на картинку
       и запрос разрешений(авторизацию) - Соглашается на всё :).

    :param ctx: Экземпляр Auth, в котором вызывается функция.

    :param params: Словарь параметров(поле params экземпляра обЪекта formparser.FormParser)
                  Содержит вспомогательные поля формы,
                  (например в случае если
                  запрашивается капча, содержит поле 'captcha_sid' которое
                   требуется для получения картинки капчи )
                   и пустые поля, те которые являются полями формы, котороые нужно заполнить.

    :param key: Имя поля формы для которого нужно вернуть значение.
    :return:
    """
    if is_an_need_auth(params):
        return ctx.password if key == 'pass' else ctx.data[key]
        # !!Кроме обработки поля "pass"
        # происходит и неявная обработка поля "email"
    if is_an_need_captcha_key(params):
        return get_captcha_data(ctx, params)
    if is_an_need_two_fact_auth(params):
        return input('Enter security code for two-factor authentication: ')
    if is_allow_access(ctx, params):
        ctx.is_allow = True
        return {}
