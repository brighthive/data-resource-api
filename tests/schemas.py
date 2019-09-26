custom_descriptor = {
  "api": {
    "resource": "tests",
    "methods": [
      {
        "get": {
          "enabled": True,
          "secured": False,
          "grants": []
        }
      }
    ]
  },
  "datastore": {
    "tablename": "tests",
    "restricted_fields": [],
    "schema": {
      "fields": [
        {
          "name": "id",
          "title": "Test ID",
          "description": "Test Desc",
          "type": "integer",
          "required": True
        },
        {
          "name": "name",
          "title": "namename",
          "description": "test name",
          "type": "string",
          "required": True
        }
      ],
      "primaryKey": "id"
    }
  }
}