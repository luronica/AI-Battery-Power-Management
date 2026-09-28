"""Loaded automatically by `gunicorn app:app` from the repository root."""

import os

bind = f"0.0.0.0:{int(os.environ.get('PORT', '8000'))}"
# Estimators and the simulator share in-memory state: keep exactly one process.
workers = 1
worker_class = "gthread"
threads = 4
preload_app = False
timeout = 60
graceful_timeout = 30
accesslog = "-"
errorlog = "-"


def post_worker_init(worker):
    worker.wsgi.extensions["battery_service"].start()


def worker_exit(server, worker):
    application = getattr(worker, "wsgi", None)
    if application is not None:
        application.extensions["battery_service"].stop()
