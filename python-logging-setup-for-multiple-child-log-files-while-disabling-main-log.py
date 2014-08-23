import logging


DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"
DEFAULT_LOG_LEVEL = logging.INFO


class DynamicHandlerLogger(logging.Logger):
    selector = "server"

    def __init__(self, name, level=logging.NOTSET, handler_factory=None):
        super(DynamicHandlerLogger, self).__init__(name, level=level)
        self.handler_factory = handler_factory
        self._handler_cache = {}

    def handle(self, record):
        selector = getattr(record, self.selector, None)
        if selector and selector not in self._handler_cache:
            newHandler = self.handler_factory(self.name, selector)
            self.addHandler(newHandler)
            self._handler_cache[selector] = newHandler
        return super(DynamicHandlerLogger, self).handle(record)


def server_filter(record):
    server = getattr(record, "server", None)
    return True if server else False


class ServerFilter(logging.Filter):
    def __init__(self, server_name, name=''):
        super(ServerFilter, self).__init__(name=name)
        self.server_name = server_name

    def filter(self, record):
        server = getattr(record, "server", None)
        if server and server == self.server_name:
            return True
        return False


class MainFilter(logging.Filter):
    def filter(self, record):
        return not server_filter(record)


def file_handler_factory(name, selector):
    handler = logging.FileHandler(filename="%s.%s.log"%(name, selector), encoding="utf-8", mode="a")
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    handler.setFormatter(formatter)
    handler.addFilter(ServerFilter(selector))
    return handler


logger = DynamicHandlerLogger("my.company", handler_factory=file_handler_factory)
logger.setLevel(DEFAULT_LOG_LEVEL)
handler = logging.FileHandler(filename="my.company.log", encoding="utf-8", mode="a")
handler.addFilter(MainFilter())
handler.setLevel(DEFAULT_LOG_LEVEL)
formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
handler.setFormatter(formatter)
logger.addHandler(handler)


def process(server):
    server_logger = logging.LoggerAdapter(logger, {'server': server})
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
