from inventory_api_app.extensions import celery


@celery.task
def dummy_task():
    return "OK"
