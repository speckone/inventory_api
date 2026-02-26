from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from inventory_api_app.models.settings import AppSetting
from inventory_api_app.extensions import db


class AppSettingList(Resource):
    """All settings as a flat dict
    ---
    get:
      tags:
        - api
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  settings:
                    type: object
    """

    method_decorators = [jwt_required()]

    def get(self):
        settings = AppSetting.query.all()
        result = {}
        for s in settings:
            if "password" in s.key:
                result[s.key] = "********" if s.value else None
            else:
                result[s.key] = s.value
        return {"settings": result}


class AppSettingResource(Resource):
    """Single setting upsert
    ---
    put:
      tags:
        - api
      parameters:
        - in: path
          name: key
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                value:
                  type: string
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                  key:
                    type: string
                  value:
                    type: string
    """

    method_decorators = [jwt_required()]

    def put(self, key):
        value = request.json.get("value")

        # Skip update if masked password value is sent back
        if "password" in key and value == "********":
            return {"msg": "setting unchanged", "key": key}

        setting = db.session.get(AppSetting, key)
        if setting:
            setting.value = value
        else:
            setting = AppSetting(key=key, value=value)
            db.session.add(setting)
        db.session.commit()

        return {"msg": "setting updated", "key": key, "value": value}
