import json
import datetime


def unknown_field_json_converter(o):
    if isinstance(o, datetime.datetime):
        return str(o.isoformat()) + "Z"
    if isinstance(o, datetime.date):
        return str(o.isoformat())


def safe_json_dumps(json_dict):
    """This will add explicit conversions for types to json.dumps
    """
    return json.dumps(json_dict, default=unknown_field_json_converter)
