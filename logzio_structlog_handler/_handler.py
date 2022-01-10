import datetime
import json
import logging
import logging.handlers
import os
import platform
import threading
import traceback
from typing import Dict

from logzio.exceptions import LogzioException
from logzio.sender import LogzioSender


class LogzIoStructlogHandler(logging.Handler):
    def __init__(
        self,
        token,
        logs_drain_timeout=3,
        url="https://listener.logz.io:8071",
        debug=False,
        backup_logs=True,
        network_timeout=10.0,
        tags: Dict[str, str] = None,
    ):

        if not token:
            raise LogzioException("Logz.io Token must be provided")

        self.logzio_sender = LogzioSender(
            token=token,
            url=url,
            logs_drain_timeout=logs_drain_timeout,
            debug=debug,
            backup_logs=backup_logs,
            network_timeout=network_timeout,
        )

        self.additional_data = {
            "host": platform.node(),
            "pid": os.getpid(),
            "tid": threading.get_ident(),
        }
        if tags:
            self.additional_data.update(tags)
        logging.Handler.__init__(self)

    def __del__(self):
        del self.logzio_sender

    @staticmethod
    def extra_fields(message):

        not_allowed_keys = (
            "args",
            "asctime",
            "created",
            "exc_info",
            "stack_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "msecs",
            "message",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "thread",
            "threadName",
        )

        var_type = (str, bool, dict, float, int, list, type(None))

        extra_fields = {}

        for key, value in message.items():
            if key not in not_allowed_keys:
                if isinstance(value, var_type):
                    extra_fields[key] = value
                else:
                    extra_fields[key] = repr(value)

        return extra_fields

    def flush(self):
        self.logzio_sender.flush()

    def format(self, record):
        message = super(LogzIoStructlogHandler, self).format(record)
        try:
            return json.loads(message)
        except (TypeError, ValueError):
            return message

    @staticmethod
    def format_exception(exc_info):
        return "\n".join(traceback.format_exception(*exc_info))

    def format_message(self, message):
        now = datetime.datetime.utcnow()
        timestamp = (
            now.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % (now.microsecond / 1000) + "Z"
        )

        # in case a msg is a Request format the message to hold the event + path
        if isinstance(message.msg, dict):
            if message.msg.get("request"):
                log_message = f"{message.msg.get('event')} FOR {message.msg['request']}"
            else:
                log_message = message.msg.get("event", "unknown message")
        else:
            log_message = message.getMessage()

        return_json = {
            "logger": message.name,
            "line_number": message.lineno,
            "path_name": message.pathname,
            "log_level": message.levelname,
            "message": log_message,
            "@timestamp": timestamp,
        }

        if message.exc_info:
            return_json["exception"] = self.format_exception(message.exc_info)

            # We want to ignore default logging formatting on exceptions
            # As we handle those differently directly into exception field
            message.exc_info = None
            message.exc_text = None

        if isinstance(message.msg, dict):
            return_json.update(self.extra_fields(message.msg))

        # Add tags to return json
        return_json.update(self.additional_data)

        return return_json

    def emit(self, record):
        self.logzio_sender.append(self.format_message(record))
