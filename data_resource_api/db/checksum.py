"""A data model for tracking the state of data resources.

"""

from data_resource_api.db import Base
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func


class Checksum(Base):
    """Data Resource Checksum

    This class is used for keeping track of the checksums associated with each data resource.
    It is used to prevent data migrations for data resources from being overwritten if they
    haven't been changed.

    """
    __tablename__ = 'checksums'
    data_resource = Column(String, primary_key=True)
    model_checksum = Column(String, nullable=False)
    api_checksum = Column(String, nullable=False)
    date_modified = Column(DateTime, default=func.now())
