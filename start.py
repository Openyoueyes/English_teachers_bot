import logging

from data import main

from data.config import APP_NAME

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":

    if APP_NAME:
        main.webhook()
    else:
        main.poll()
