from flask import Flask, request, g
import time
import logging
import datetime

# Custom filter to remove OpenAI API logs
class APILogFilter(logging.Filter):
    def filter(self, record):
        # Filter out OpenAI API logs and similar HTTP client logs
        if "api.openai.com" in getattr(record, "msg", ""):
            return False
        return True


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("flask-morgan")

root_logger = logging.getLogger()
root_logger.addFilter(APILogFilter())

logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

TINY = ":method :url :status :response-time ms"
DEV = "[:datetime] :method :url :status :response-time ms"

class FlaskMorgan:
    def __init__(self, app=None, format_string=None, log_file=None):
        """
        Initialize the Flask-Morgan logger

        :param app: Flask application instance
        :param format_string: Format string (similar to Morgan)
        :param log_file: Optional file path to write logs to
        """
        self.format_string = format_string or DEV

        # Configure file logging if requested
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter("%(message)s"))
            logger.addHandler(file_handler)

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize the logger with a Flask application

        :param app: Flask application instance
        """

        # Before request handler
        @app.before_request
        def before_request():
            g.start_time = time.time()

        # After request handler
        @app.after_request
        def after_request(response):
            if hasattr(g, "start_time"):
                self._log_request(response)
            return response

    def _log_request(self, response):
        """
        Log the request details based on the format string

        :param response: Flask response object
        """
        duration = time.time() - g.start_time
        duration_ms = round(duration * 1000, 2)

        # Get datetime
        now = datetime.datetime.now()

        # Prepare tokens mapping
        tokens = {
            ":remote-addr": request.remote_addr or "-",
            ":method": request.method,
            ":url": request.path,
            ":http-version": request.environ.get("SERVER_PROTOCOL", "HTTP/1.1"),
            ":status": response.status_code,
            ":response-time": duration_ms,
            ":date": now.strftime("%d/%b/%Y"),
            ":time": now.strftime("%H:%M:%S"),
            ":datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            ":user-agent": request.headers.get("User-Agent", "-"),
            ":referrer": request.headers.get("Referer", "-"),
            ":content-length": response.headers.get("Content-Length", "-"),
        }

        # Replace tokens in format string
        log_message = self.format_string
        for token, value in tokens.items():
            log_message = log_message.replace(token, str(value))
        # Log the message
        logger.info(log_message)


# For backward compatibility
def request_logger(format_string=None):
    def middleware(app):
        FlaskMorgan(app, format_string=format_string)
        return app

    return middleware