import logging


DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"
DEFAULT_LOG_LEVEL = logging.INFO


class HandlerPerChildLogger(logging.Logger):
    selector = "server"

    def __init__(self, name, handler_factory, level=logging.NOTSET):
        super(HandlerPerChildLogger, self).__init__(name, level=level)
        self.handler_factory = handler_factory

    def getChild(self, suffix):
        logger = super(HandlerPerChildLogger, self).getChild(suffix)
        if not logger.handlers:
            logger.addHandler(self.handler_factory(logger.name))
            logger.setLevel(DEFAULT_LOG_LEVEL)
        return logger


def file_handler_factory(name):
    handler = logging.FileHandler(filename="{}.log".format(name), encoding="utf-8", mode="a")
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    handler.setFormatter(formatter)
    return handler


logger = HandlerPerChildLogger("my.company", file_handler_factory)
logger.setLevel(DEFAULT_LOG_LEVEL)
handler = logging.FileHandler(filename="my.company.log", encoding="utf-8", mode="a")
handler.setLevel(DEFAULT_LOG_LEVEL)
formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
handler.setFormatter(formatter)
logger.addHandler(handler)


def process(server):
    server_logger = logger.getChild(server)
    server_logger.info("This should show up only in the server-specific log file for %s", server)
    server_logger.info("another log message for %s", server)


def main():
    # servers list retrieved from another function, just here for iteration
    servers = ["server1", "server2", "server3"]

    logger.info("This should show up in the console and main.log.")

    for server in servers:
        process(server)

    logger.info("This should show up in the console and main.log again.")


if __name__ == "__main__":
    main()
