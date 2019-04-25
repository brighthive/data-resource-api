"""A data model for tracking the state of data resources.

"""

from data_resource_api.db import Base
from sqlalchemy import Column, String, MetaData


class Checksum(Base):
    __tablename__ = 'checksums'
    data_resource = Column(String, primary_key=True)
    checksum = Column(String, nullable=False)
