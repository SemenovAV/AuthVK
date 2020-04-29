from urllib.parse import urlencode


def auth(session: any, config: dict, auth_url: str = None, user_agent: str = None) -> any:
    auth_url = auth_url or 'https://oauth.vk.com/authorize'
    user_agent = user_agent or 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'

    params = urlencode(config)
    auth_url = f'{auth_url}?{params}'
    session.headers.update({
        'User-agent': user_agent
    })
    return session.get(auth_url)
