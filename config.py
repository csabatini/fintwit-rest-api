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
