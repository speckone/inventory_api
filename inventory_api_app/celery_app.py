from inventory_api_app.app import init_celery

app = init_celery()
app.conf.imports = app.conf.imports + ("inventory_api_app.tasks.example",)
