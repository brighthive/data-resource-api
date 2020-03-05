"""
"""

from data_resource_api.db import Base
from sqlalchemy import Column, String, Binary


class Migrations(Base):
    """

    """
    __tablename__ = 'migrations'
    file_name = Column(String, primary_key=True)
    file_pickle = Column(Binary, nullable=False)
