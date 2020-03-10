import os
from data_resource_api.app.utils.descriptor import DescriptorsGetter
from data_resource_api.db import Session, Checksum
from data_resource_api.app.utils.db_handler import DBHandler
from data_resource_api.logging import LogFactory

logger = LogFactory.get_console_logger('backwards-compat')

# This will upgrade the DB of a 1.0.4 version (or earlier?) database
# to be compatible with the 1.1.0 version.
#
# The following manual steps need to occur before running the upgrade script.
#
#     Update alembic version number to match the new first migration — e56a6f702357
#     Change the down_revision for the second migration to the new first migration — e56a6f702357
#     Change the alembic_version to the most recent migration you have
#
# DELETE FROM alembic_version;
# INSERT INTO alembic_version(version_num) VALUES (‘123456789ABCDEF’);
#
# You can now run the upgrade script. Do this by when running the DMM setting the parameter from --data-model-manager to --upgrade

SCHEMA_DIR = "/data-resource/schema"
MIGRATION_DIR = "/data-resource/migrations/versions"


# Do we need to perform this upgrade checks
def check_for_checksum_column():
    session = Session()
    query = """
    SELECT 1
    FROM information_schema.columns
    WHERE table_name='checksums' and column_name='descriptor_json'
    """
    rs = session.execute(query)

    count = 0
    for _row in rs:
        count += 1

    if count == 1:
        print("Found the descriptor_json column -- skipping import")
        return True

    return False


def check_for_migrations_table():
    session = Session()
    query = """
    SELECT 1
    FROM information_schema.tables
    WHERE table_name='migrations';
    """
    rs = session.execute(query)

    count = 0
    for _row in rs:
        count += 1

    if count == 1:
        print("Found the descriptor_json column -- skipping import")
        return True

    return False


# Create the changes to DB
def upgrade_checksum():
    session = Session()
    query = """
    ALTER TABLE checksums ADD COLUMN descriptor_json jsonb;
    """
    try:
        session.execute(query)
        session.commit()
    except BaseException:
        logger.exception('Failed to upgrade checksum')


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
        session.commit()
    except BaseException:
        logger.exception('Failed to create table migrations')


# Push the required data to the DB
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
            logger.exception('Error pushing descriptors')
            continue


def push_migrations():
    migrations = [f for f in os.listdir(MIGRATION_DIR) if f.endswith('.py')]
    for file_name in migrations:
        if 'create_table_checksum_and_logs' in file_name:
            continue

        full_file_path = os.path.join(MIGRATION_DIR, file_name)
        with open(full_file_path, 'rb') as file_:
            DBHandler.save_migration(full_file_path, file_.read())


if not check_for_checksum_column():
    # upgrade the checksum table
    upgrade_checksum()
    # iter over schema -- push all descriptors
    push_descriptors()
    logger.info("Done with checksums...")

if not check_for_migrations_table():
    # create migration table
    create_migrations()
    # iter over dir --- push all migrations
    push_migrations()
    logger.info("Done with migrations...")

logger.info("Done! You are ready to run the normal Data Model Manager :D")
