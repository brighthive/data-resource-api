custom_descriptor = [{
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
] ## I think this can be deleted

frameworks_descriptor = {
    "api": {
      "resource": "frameworks",
      "methods": [
        {
          "get": {
            "enabled": True,
            "secured": False,
            "grants": []
          },
          "post": {
            "enabled": True,
            "secured": False,
            "grants": []
          },
          "custom": [
            {
              "resource": "/frameworks/skills",
              "methods": [
                {
                  "get": {
                    "enabled": True,
                    "secured": False,
                    "grants": []
                  },
                  "put": {
                    "enabled": True,
                    "secured": False,
                    "grants": []
                  },
                  "patch": {
                    "enabled": True,
                    "secured": False,
                    "grants": []
                  },
                  "delete": {
                    "enabled": True,
                    "secured": False,
                    "grants": []
                  }
                }
              ]
            }
          ]
        }
      ]
    },
    "datastore": {
      "tablename": "frameworks",
      "restricted_fields": [],
      "schema": {
        "fields": [
          {
            "name": "id",
            "title": "framework ID",
            "description": "framework Desc",
            "type": "integer",
            "required": False
          },
          {
            "name": "name",
            "title": "framework name",
            "description": "framework name",
            "type": "string",
            "required": True
          },
          {
            "name": "jsonb",
            "title": "jsonb",
            "type": "object",
            "required": False
          }
        ],
        "primaryKey": "id"
      }
    }
  }

skills_descriptor = {
    "api": {
      "resource": "skills",
      "methods": [
        {
          "get": {
            "enabled": True,
            "secured": False,
            "grants": []
          },
          "post": {
            "enabled": True,
            "secured": False,
            "grants": []
          }
        }
      ]
    },
    "datastore": {
      "tablename": "skills",
      "restricted_fields": [],
      "schema": {
        "fields": [
          {
            "name": "id",
            "title": "skill ID",
            "description": "skill Desc",
            "type": "integer",
            "required": False
          },
          {
            "name": "text",
            "title": "skill text",
            "description": "skill text",
            "type": "string",
            "required": True
          }
        ],
        "primaryKey": "id"
      }
    }
  }
