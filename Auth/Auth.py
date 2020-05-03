from typing import Dict, Callable
from urllib.parse import urlencode

import requests

from .form_data_handlers.handler import handler
from .formparser import FormParser
from .logger.get_logger import logger as log


class Auth:
    """
    Класс для получения OAuth-токена в VK. Для получения токена
       требуется аунтефикация.
    """
    config: Dict[str, str]
    user_agent: str
    auth_url: str
    login: str
    password: str
    session: any
    logger: any
    auto: bool
    form_data_handler: Callable

    def __init__(self,
                 config=None,
                 user_agent='Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0',
                 auth_url='https://oauth.vk.com/authorize',
                 login=None,
                 password=None,
                 logger=log,
                 auto=True,
                 form_data_handler=handler

                 ):
        """
        Метод принимает параметры для отправки запроса, для получения
         OAuth-токена на сервер VK.

        :param config: (необязательный параметр) Конфигурация в формате:
                {
                'client_id': '7395093' - id приложения для которого получается
                                          токен
                'scope': 'friends,groups,offline', - Разрешения которые
                                                      требуются приложению
                'redirect_uri': 'https://oauth.vk.com/blank.html', - Редирект
                                    урл указанный в настройках приложения или,
                                    как в данном случае, урл по умолчанию.
                'v': '5.103' - Версия апи
                }
        :param user_agent: (необязательный параметр) Строка user-agent.
        :param auth_url: (необязательный параметр) Урл сервера OAuth авторизации VK.
        :param login: Логин для аунтентификации в VK.
        :param password: Пароль для аунтефикации в VK.
        :param logger: Python логгер.
        :param auto: Включает основной рабочий режим, при котором обрабатывается
                функция переданная параметром form_data_handler.
                При auto == False form_data_handler не используется.
                Скрипт работает в тестовом режиме при котором удобно делать отладку.
                 Первым вызывается метод get_login_form,
                далее по очеридиб для каждой формы:
                    1.parse_form - для обработки полей формы требующих внимания.
                          метод принимает один параметр - функцию обработчик.
                    2.submit_form - для отправки обработанной формы.
        :param form_data_handler: Обработчик данных приходящих с сервера. В Функцию передается три параметра:
            1. Контекст - этот объект.
            2. Словарь параметров полученный из парсера форм - то что надо обработать.
            3. Поле из словаря параметров, которое обрабатывается.
        Пример:
        Обработка аунтификации.
          Если в словаре params есть поля "email" и "pass" - требуется аунтефикация,
            если обрабатывается поле "pass" (третьий параметр key == "pass") - отдаем поле password объекта,
            если нет отдаем поле email объекта.

            def handler(ctx, params, key):
                if 'email' in params and 'pass' in params:
                    return ctx.password if key == 'pass' else ctx.email
        """
        self.config = config or {}
        self.user_agent = user_agent
        self.auth_url = auth_url
        self.email = login
        self.password = password
        self.session = requests.Session()
        self.main_url = 'https://m.vk.com'
        self.login_url = 'https://login.vk.com'
        self.logger = logger
        self.parser = None
        self.next_url = None
        self.next_params = None
        self.response = None
        self.state = True
        self.error = None
        self.form_data_handler = form_data_handler
        self.auto = auto
        self.data = self.__dict__
        self.is_allow = False

    def get_auth(self):
        """
        Основной метод - запускает цикл обработки форм.

        :return: При auto == True:
             Словарь {
                'access_token': OAuth-токен,
                'user_id': id пользователя для которого выдан токен,
                'session': Requests сесия.
        }
                 При auto == False:
                  возвращает экземпляр объекта.
        """
        self.get_login_form()
        while self.is_allow is False:
            self.parse_form().submit_form()
        if self.auto:
            return self._get_access_data()
        else:
            return self

    def parse_form(self, callback=None):
        """
        Метод запускает парсинг формы активной в данный момент.

        :param callback: Если параметр auto == False, принимает функцию
                         обработчик формы.
        :return: При удачном исходе  - экземпляр объекта.
                 Если ошибка - вернет None
        """
        if self.auto:
            callback = self.form_data_handler
        if self.state:
            self.logger.info('Start parsing')
            self.parser = FormParser()
            parser = self.parser
            try:
                parser.feed(str(self.response.text))
                self.logger.debug(parser.params)
                self.logger.info('Get response.')
                self.next_params = {}
                if len(parser.params) > 0:
                    for (key, value) in parser.params.items():
                        self.logger.info(f'Get key {key}...')
                        if not value:
                            val = callback(self, parser.params, key) if callback else self.data.get(key)
                            self.next_params[key] = val
                            self.logger.info(f'Set key {key} as self.next key.')
                else:
                    callback(self, parser.params, None)

                if parser.url:
                    if self.login_url not in parser.url:
                        self.next_url = f'{self.main_url}{self.parser.url}'
                    else:
                        self.next_url = self.parser.url
                    self.logger.info(f'Set self.next url: {self.next_url}.')
                self.state = True
                self.logger.info(self.state)
                return self
            except Exception as e:
                self.logger.exception(e)
                self.state = False
                self.error = e

    def get_login_form(self) -> any:
        """
        Метод получает данные формы входа в VK для аунтефикации,
         для получения токена
        :return: Экземпляр обЪекта
        """
        self.logger.info('Get login form.')
        if self.state:
            config: dict = self.config or {
                'client_id': '7395093',
                'scope': 'friends,groups,offline',
                'redirect_uri': 'https://oauth.vk.com/blank.html',
                'v': '5.103',
            }
            if not self.config:
                self.config.update(config)
            config.update({
                'display': 'wap',
                'response_type': 'token',
            }),
            params = urlencode(config)
            self.session.headers.update({'User-agent': self.user_agent})
            self.logger.info('Set config...')
            try:
                self.logger.info('Get response.')
                self.response = self.session.get(f'{self.auth_url}?{params}')
                self.state = True
                self.logger.info(self.state)
                return self
            except requests.exceptions.BaseHTTPError as e:
                self.logger.exception(e)
                self.state = False
                self.error = e

    def submit_form(self):
        """
        Метод отправляет данные обработтанной формы.
        :return: Экземпляр обьекта.
        """
        self.logger.info('Submit form.')
        parser = self.parser
        if parser.method == 'post':
            self.logger.info('Configuration.')
            payload = parser.params
            payload.update(self.next_params)
            self.logger.info('Configuration.True.')
            try:
                self.logger.info('Post data...')
                self.logger.debug(f'url: {self.next_url}')
                self.logger.debug(f'payload:{payload}')
                self.response = self.session.post(self.next_url, data=payload)
                self.next_params = {}
                self.state = True
                self.logger.info('Post data.True.')
                self.logger.info('True.')
                return self
            except requests.exceptions.BaseHTTPError as e:
                self.logger.info(e)
                self.state = False
                self.error = e

    def _get_access_data(self) -> object:
        """
        Функция вызывается после обработки всех форм. Парсит  урл с токеном.

        :return: Словарь {
                'access_token': OAuth-токен,
                'user_id': id пользователя для которого выдан токен,
                'session': Requests сесия.
                'scope': Разрешения на которые распрастраняется токен
                'v': версия апи
        }
        """
        try:
            params = self.response.url.split('#')[1].split('&')
            return {
                'access_token': params[0].split('=')[1],
                'user_id': params[2].split('=')[1],
                'session': self.session,
                'scope': self.config['scope'],
                'v': self.config['v']
            }
        except IndexError as err:
            return False
