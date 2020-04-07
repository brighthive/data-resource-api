import os

from alembic import command
from data_resource_api.db import Checksum, Migrations, Session
from data_resource_api.logging import LogFactory


logger = LogFactory.get_console_logger("db-handler")


class DBHandler:
    def __init__(self, config):
        self.config = config

    def add_model_checksum(
        self, table_name: str, model_checksum: str = "0", descriptor_json: dict = {}
    ):
        """Adds a new checksum for a data model.

        Args:
            table_name (str): Name of the table to add the checksum.
            checksum (str): Checksum value.
        """
        session = Session()
        try:
            checksum = Checksum()
            checksum.data_resource = table_name
            checksum.model_checksum = model_checksum
            checksum.descriptor_json = descriptor_json
            session.add(checksum)
            session.commit()
        except Exception:
            logger.exception("Error adding checksum")
        finally:
            session.close()

    def update_model_checksum(
        self, table_name: str, model_checksum: str, descriptor_json: dict = {}
    ):
        """Updates a checksum for a data model.

        Args:
            table_name (str): Name of the table to add the checksum.
            checksum (str): Checksum value.

        Returns:
            bool: True if checksum was updated. False otherwise.
        """
        session = Session()
        updated = False
        try:
            checksum = (
                session.query(Checksum)
                .filter(Checksum.data_resource == table_name)
                .first()
            )
            checksum.model_checksum = model_checksum
            checksum.descriptor_json = descriptor_json
            session.commit()
            updated = True
        except Exception:
            logger.exception("Error updating checksum")
        finally:
            session.close()
        return updated

    def get_model_checksum(self, table_name: str):
        """Retrieves a checksum by table name.

        Args:
            table_name (str): Name of the table to add the checksum.

        Returns:
            object: The checksum object if it exists, None otherwise.
        """
        session = Session()
        checksum = None
        try:
            checksum = (
                session.query(Checksum)
                .filter(Checksum.data_resource == table_name)
                .first()
            )
        except Exception:
            logger.exception("Error retrieving checksum")
        finally:
            session.close()
        return checksum

    def get_stored_descriptors(self) -> list:
        """Gets stored json models from database.

        Returns:
            list: List of JSON dictionaries
        """
        session = Session()
        descriptor_list = []  # list of json dict
        try:
            query = session.query(Checksum)
            for _row in query.all():
                try:
                    if not _row.descriptor_json:
                        continue
                except Exception:
                    logger.exception(
                        "Checksum table or row does not have a value for the descriptor_json column."
                    )

                descriptor_list.append(_row.descriptor_json)

        except Exception:
            logger.info("Error retrieving stored models")
        finally:
            session.close()

        return descriptor_list

    def get_stored_checksums(self) -> list:
        session = Session()
        checksums = []  # list of json dict
        try:
            query = session.query(Checksum)
            for _row in query.all():
                checksums.append((_row.data_resource, _row.model_checksum))
        except Exception:
            logger.exception("Error retrieving stored models")
        finally:
            session.close()

        return checksums

    def upgrade(self):
        """Migrate up to head.

        This method runs  the Alembic upgrade command programatically.
        """
        alembic_config, migrations_dir = self.config.get_alembic_config()
        if migrations_dir is not None:
            command.upgrade(config=alembic_config, revision="head")
        else:
            logger.info("No migrations to run...")

    def revision(self, table_name: str, create_table: bool = True):
        """Create a new migration.

        This method runs the Alembic revision command programmatically.
        """
        alembic_config, migrations_dir = self.config.get_alembic_config()
        if migrations_dir is not None:
            if create_table:
                message = "Create table {}".format(table_name)
            else:
                message = "Update table {}".format(table_name)
            command.revision(config=alembic_config, message=message, autogenerate=True)
        else:
            logger.info("No migrations to run...")

    @staticmethod
    def save_migration(file_name: str, file_blob) -> None:
        """This function is called by alembic as a post write hook.

        It will take a migration file and save it to the database.
        """
        logger.info("Trying to save migration files to DB...")
        session = Session()
        try:
            new_migration = Migrations()
            new_migration.file_name = file_name
            new_migration.file_blob = file_blob
            result = (
                session.query(Migrations)
                .filter(Migrations.file_name == file_name)
                .count()
            )
            if result == 0:
                session.add(new_migration)
                session.commit()
        except Exception:
            logger.exception("Failed to save migration files to DB.")
        finally:
            session.close()

    def get_migrations_from_db_and_save_locally(self) -> None:
        logger.info("Restoring migration files from DB...")
        session = Session()
        try:
            query = session.query(Migrations)
            for _row in query.all():
                self.save_migrations_to_local_file(_row.file_name, _row.file_blob)
        except Exception:
            logger.info("Failed to restore migration files from DB.")
        finally:
            session.close()

    def save_migrations_to_local_file(self, file_name: str, file_blob) -> None:
        file_name = os.path.basename(file_name)
        _, migration_file_dir = self.config.get_alembic_config()
        full_migration_file_path = os.path.join(migration_file_dir, file_name)

        with open(full_migration_file_path, "wb") as file_:
            file_.write(file_blob)
