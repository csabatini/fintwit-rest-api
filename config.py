LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    },
    'formatters': {
        'json': {
            'format': ("{\"timestamp\": \"%(asctime)s\", \"level\": \"%(levelname)s\","
                       "\"message\": %(message)s}"),
            'datefmt': '%Y-%m-%dT%H:%M:%SZ'
        }
    },
    'handlers': {
        'console': {
            'formatter': 'json',
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        }
    }
}

DEFAULT_IDS = [
    20402945, # CNBC
    26574283, # CNBCnow
    36992781, # CNBCPro
    1278852289, # TradingNation
    16451932, # MadMoneyOnCNBC
    69620713 # BloombergMarkets
]