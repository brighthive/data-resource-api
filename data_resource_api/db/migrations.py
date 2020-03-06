"""
"""

from data_resource_api.db import Base
from sqlalchemy import Column, String, LargeBinary


class Migrations(Base):
    """

    """
    __tablename__ = 'migrations'
    file_name = Column(String, primary_key=True)
    file_blob = Column(LargeBinary, nullable=False)
