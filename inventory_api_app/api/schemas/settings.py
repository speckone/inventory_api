from inventory_api_app.models.settings import AppSetting
from inventory_api_app.extensions import ma


class AppSettingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AppSetting
        load_instance = True
