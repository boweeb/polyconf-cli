import logging.config

import click
from rich.console import Console
from rich.traceback import install as rich_traceback_install


console = Console(
    log_time=False,
    # width=192,
    stderr=True,
)

CONFIG_DATA = {
    "version": 1,
    "formatters": {
        "rich_fmt": {
            "format": "%(message)s",
            # "format": "%(message)s \t <%(name)s.%(funcName)s()>",
            # "datefmt": " ",
        },
    },
    "handlers": {
        "rich": {
            "class": "rich.logging.RichHandler",
            "level": "DEBUG",
            "console": console,
            "formatter": "rich_fmt",
            "show_time": False,
            # "keywords": ["foo", "bar"],
        },
    },
    "loggers": {
        "boto3": {"propagate": "no"},
        "botocore": {"propagate": "no"},
        "urllib3": {"propagate": "no"},
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["rich"],
    },
}

logging.config.dictConfig(CONFIG_DATA)

rich_traceback_install(
    console=console,
    suppress=[
        click,
    ],
    show_locals=True
)
