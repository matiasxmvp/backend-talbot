# gunicorn_config.py - Configuración para Gunicorn con FastAPI/Uvicorn
import multiprocessing

bind = "0.0.0.0:8080"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True