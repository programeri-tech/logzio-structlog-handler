# logzio-structlog-handler

Handler to send structlog logger to logzio

All logs have `host`, `pid` and `tid` added to them.

Example of log created with handler:

```python
logger.info(
    "request_finished",
    request=f"{METHOD} {ENDPOINT}",
    code=response.status_code,
    request_id=uuid4()
)
```
Logzio:
```shell
  "_source": {
    "request": "GET /account/ping",
    "code": 200,
    "level": "info",
    "logger": "django_structlog.middlewares.request",
    "ip": "127.0.0.1",
    "log_level": "INFO",
    "pid": 1,
    "type": "http-bulk",
    "message": "request_finished FOR GET /account/ping",
    "tid": [
      140649178957632
    ],
    "tags": [
      "_logz_http_bulk_json_8070"
    ],
    "@timestamp": "2022-01-10T19:34:19.932Z",
    "line_number": 71,
    "host": "name-of-host",
    "event": "request_finished",
    "request_id": "3777349e-0247-4c89-ace2-ea2174930f39",
    "path_name": "path/to/file.py",
    "timestamp": "2022-01-10T19:34:19.931955Z",
    "random_tag_1": "some_value",
    "random_tag_2": 123
  }
```

## Instructions:

1. Install

```shell
❯ pip install logzio-structlog-handler
```

2. Add the following handler to you LOGGING file:

```python    
LOGGING = {
    "handlers": {
        "logzio": {
            "class": "logzio-structlog-handler.LogzIoStructlogHandler",
            "level": "INFO",
            "token": "YOUR_TOKEN",
            "logs_drain_timeout": 5,
            "url": "https://listener.logz.io:8071",
            "network_timeout": 10,
            # accepts any Dict[str, Any] value and passes it to all logs
            "tags": {"random_tag_1": "some_value", "random_tag_2": 123},
        }
    },
    "loggers": {
        "": {"level": "INFO", "handlers": ["logzio"], "propagate": True},
    },
}   
```
