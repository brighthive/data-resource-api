"""A mapping of Frictionless Table Schema data types to SQLAlchemy data types

"""

from sqlalchemy import Integer, String, Float, Boolean, Date, DateTime

# Mapping of a Frictionless Table Schema to SQLAlchemy Data Type.
#
# Note:
#   Only a subset of Table Schema elements are mapped to SQLAlchemy data types.
#   See: https://frictionlessdata.io/specs/table-schema/
#
TABLESCHEMA_TO_SQLALCHEMY_TYPES = {
    'string': String,
    'number': Float,
    'integer': Integer,
    'boolean': Boolean,
    'object': String,
    'array': String,
    'date': Date,
    'time': DateTime,
    'datetime': DateTime,
    'year': Integer,
    'yearmonth': Integer,
    'duration': Integer,
    'geopoint': String,
    'geojson': String,
    'any': String
}
