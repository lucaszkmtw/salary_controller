from project.settings.settings import LOGLEVEL
bind = "0.0.0.0:8000"
workers = 4

accesslog = "/usr/src/app/logs/gunicorn.access.log"
errorlog = "/usr/src/app/logs/gunicorn.error.log"

capture_output = True

loglevel = LOGLEVEL
