import logging


class Log:
    logging.basicConfig(level=logging.INFO,
                        format="\033[0;30m[%(asctime)s] %(levelname)s | \033[0m%(message)s",
                        datefmt="%y-%m-%d %H:%M:%S")

    @staticmethod
    def info(message: str):
        logging.info("\033[0;32m" + message + "\033[0m")

    @staticmethod
    def warn(message: str):
        logging.warning("\033[0;33m" + message + "\033[0m")

    @staticmethod
    def error(message: str):
        logging.error("\n\033[0;31m"+"-" * 23 + '\n| ' + message + "\033[0m" + "\n" + "└"+"-" * 55)

    @staticmethod
    def debug(message: str):
        logging.debug("\033[0;37m" + message + "\033[0m")
