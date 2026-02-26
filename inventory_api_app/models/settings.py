from inventory_api_app.database import Model, Column
from inventory_api_app.extensions import db


class AppSetting(Model):
    __tablename__ = 'app_setting'
    key = Column(db.String, primary_key=True)
    value = Column(db.String, nullable=True)

    def __repr__(self):
        return f"<AppSetting {self.key}>"
