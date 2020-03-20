import json
import datetime


def unknown_field_json_converter(o):
    if isinstance(o, datetime.datetime):
        print(str(o))
        print(o.__str__())
        return str(o.isoformat()) + "Z"


def safe_json_dumps(json_dict):
    """This will add explicit conversions for types to json.dumps
    """
    return json.dumps(json_dict, default=unknown_field_json_converter)
