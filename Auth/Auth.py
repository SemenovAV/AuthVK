from typing import Dict, Callable
from urllib.parse import urlencode

import requests

from formparser import FormParser
from .logger.get_logger import logger as log


class Auth:
    config: Dict[str, str]
    user_agent: str
    auth_uri: str
    login: str
    password: str
    session: any
    logger: any
    form_data_handler: Callable

    def __init__(self,
                 config=None,
                 user_agent='Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0',
                 auth_uri='https://oauth.vk.com/authorize',
                 login=None,
                 password=None,
                 session=None,
                 logger=log,
                 form_data_handler=None
                 ):
        self.config = config
        self.user_agent = user_agent
        self.auth_uri = auth_uri
        self.email = login
        self.password = password
        self.session = session or requests.Session()
        self.main_uri = 'https://m.vk.com'
        self.login_uri = 'https://login.vk.com'
        self.logger = logger
        self.parser = None
        self.next_uri = None
        self.next_params = None
        self.response = None
        self.state = True
        self.error = None
        self.form_data_handler = form_data_handler
        self.data = self.__dict__
        self.is_allow = False

    def get_auth(self):
        self.get_login_form()
        while self.is_allow is False:
            self.parse_form().submit_form()
        return self.get_access_data()

    def parse_form(self, callback=None):
        callback = callback or self.form_data_handler
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
                    if self.login_uri not in parser.url:
                        self.next_uri = f'{self.main_uri}{self.parser.url}'
                    else:
                        self.next_uri = self.parser.url
                    self.logger.info(f'Set self.next url: {self.next_uri}.')
                self.state = True
                self.logger.info(self.state)
                return self
            except Exception as e:
                self.logger.exception(e)
                self.state = False
                self.error = e

    def get_login_form(self) -> any:
        self.logger.info('Get login form.')
        if self.state:
            config: dict = {}
            config.update({
                'client_id': '7395093',
                'scope': 'friends,groups,offline',
                'redirect_uri': 'https://oauth.vk.com/blank.html',
                'display': 'wap',
                'v': '5.103',
                'response_type': 'token',
            }),
            params = urlencode(config)
            self.session.headers.update({'User-agent': self.user_agent})
            self.logger.info('Set config...')
            try:
                self.logger.info('Get response.')
                self.response = self.session.get(f'{self.auth_uri}?{params}')
                self.state = True
                self.logger.info(self.state)
                return self
            except requests.exceptions.BaseHTTPError as e:
                self.logger.exception(e)
                self.state = False
                self.error = e

    def submit_form(self):
        self.logger.info('Submit form.')
        parser = self.parser
        if parser.method == 'post':
            self.logger.info('Configuration.')
            payload = parser.params
            payload.update(self.next_params)
            self.logger.info('Configuration.True.')
            try:
                self.logger.info('Post data...')
                self.logger.debug(f'url: {self.next_uri}')
                self.logger.debug(f'payload:{payload}')
                self.response = self.session.post(self.next_uri, data=payload)
                self.next_params = {}
                self.state = True
                self.logger.info('Post data.True.')
                self.logger.info('True.')
                return self
            except requests.exceptions.BaseHTTPError as e:
                self.logger.info(e)
                self.state = False
                self.error = e

    def get_access_data(self) -> object:
        try:
            params = self.response.url.split('#')[1].split('&')
            return {
                'access_token': params[0].split('=')[1],
                'user_id': params[2].split('=')[1],
                'session': self.session
            }
        except IndexError as err:
            return False
