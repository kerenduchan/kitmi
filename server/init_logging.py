import logging


def init_logging():
    general_log_level = logging.DEBUG
    db_log_level = logging.WARN

    logging.basicConfig(filename='kitmi.log', filemode='w', level=general_log_level)
    logging.getLogger('sqlalchemy.engine').setLevel(db_log_level)
    logging.getLogger('aiosqlite').setLevel(db_log_level)
