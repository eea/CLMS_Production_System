from airflow.config_templates.default_celery import DEFAULT_CELERY_CONFIG

CELERY_CONFIG = dict(DEFAULT_CELERY_CONFIG, **{'worker_pool_restarts': True})
