from setuptools import setup

setup(
    name='AuthVK',
    version='0.1.2',
    packages=['AuthVK', 'AuthVK.parser', 'AuthVK.form_data_handlers',],
    install_requires=['requests',]
    url='https://github.com/SemenovAV/AuthVK',
    license='',
    author='SemenovAV',
    author_email='7.on.off@bk.ru',
    description='Module for authorization and obtaining an OAuth token for your application.'
)
