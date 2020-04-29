from logging import config, getLogger

config.fileConfig('logger.config')
logger = getLogger('app')
