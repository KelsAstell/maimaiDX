import logging


class Log:
    logging.basicConfig(level=logging.INFO,
                        format="[%(asctime)s] %(levelname)s | %(message)s",
                        datefmt="%m-%d %H:%M:%S")

    @staticmethod
    def info(message: str):
        logging.info(message)

    @staticmethod
    def warn(message: str):
        logging.warning("⚠️" + message)

    @staticmethod
    def error(message: str):
        logging.error("⛝" + message)

    @staticmethod
    def debug(message: str):
        logging.debug("\033[0;37m" + message + "\033[0m")
