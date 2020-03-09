import sqlalchemy
import os
import sys
from data_resource_api.app.utils.descriptor import Descriptor, DescriptorsGetter
# POSTGRES_USER = os.env("POSTGRES_USER")
# POSTGRES_PASSWORD = os.env("POSTGRES_PASSWORD")
# POSTGRES_DATABASE = os.env("POSTGRES_DATABASE")
# POSTGRES_HOSTNAME = os.env("POSTGRES_HOSTNAME")
# POSTGRES_PORT = os.env("POSTGRES_PORT")

# SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
#     POSTGRES_USER,
#     POSTGRES_PASSWORD,
#     POSTGRES_HOSTNAME,
#     POSTGRES_PORT,
#     POSTGRES_DATABASE
# )

# engine = create_engine(SQLALCHEMY_DATABASE_URI)
from data_resource_api.db import Session, Checksum, Migrations
from data_resource_api.app.utils.db_handler import DBHandler

# TODO specify the versions that this is compatabile with
SCHEMA_DIR = "/data-resource/schema"
MIGRATION_DIR = "/data-resource/migrations/versions"

# conn = engine.connect()


# Error checking functions
def check_for_checksum_column():
    session = Session()
    query = """
    SELECT 'descriptor_json'
    FROM information_schema.columns
    WHERE table_name='checksums' and column_name='descriptor_json';
    """
    rs = session.execute(query)
    if len(rs.all()) > 0:
        sys.exit(1)


def check_for_migrations_table():
    session = Session()
    query = """
    SELECT 1
    FROM information_schema.tables
    WHERE table_name='migrations';
    """
    rs = session.execute(query)
    if len(rs.all()) > 0:
        sys.exit(1)

# create the things functions


def upgrade_checksum():
    session = Session()
    query = """
    ALTER TABLE checksums ADD COLUMN descriptor_json jsonb;
    """
    try:
        session.execute(query)
    except BaseException:
        print('Failed to upgrade checksum')


def create_migrations():
    session = Session()
    query = """
    CREATE TABLE migrations (
        file_name TEXT PRIMARY KEY,
        file_blob BYTEA
    );
    """
    try:
        session.execute(query)
    except BaseException:
        print('Failed to create table migrations')

# push the data functions


def push_descriptors():
    session = Session()

    descriptors = DescriptorsGetter([SCHEMA_DIR], [])
    for desc in descriptors.iter_descriptors():
        try:
            row = session.query(Checksum).filter(
                Checksum.data_resource == desc.table_name
            ).first()

            row.descriptor_json = desc.descriptor
            session.add(row)
            session.commit()
        except Exception:
            print('Error pushing descriptors')
            continue


def push_migrations():
    migrations = [f for f in os.listdir(MIGRATION_DIR) if f.endswith('.py')]
    for file_name in migrations:
        with open(file_name, 'rb') as file_:
            DBHandler.save_migration(file_, file_name)


check_for_checksum_column()
check_for_migrations_table()

# upgrade the checksum table
upgrade_checksum()
# iter over schema -- push all descriptors
push_descriptors()

# create migration table
create_migrations()
# iter over dir --- push all migrations
push_migrations()
