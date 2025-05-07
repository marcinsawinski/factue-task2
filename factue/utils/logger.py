import logging


def get_logger(name, level=logging.INFO):
    logging.basicConfig(
        level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logging.getLogger("luigi-interface").setLevel(level)
    return logging.getLogger(name)
