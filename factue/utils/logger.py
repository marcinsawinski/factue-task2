import logging


def get_logger(
    level=logging.INFO,
):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logging.getLogger("luigi-interface").setLevel(level)
