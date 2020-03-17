import os
import json
from data_resource_api.logging import LogFactory
from hashlib import md5

logger = LogFactory.get_console_logger('descriptor-utils')


class DescriptorsLoader():
    """
    Yields Descriptor objects when given a list and/or a directory of descriptors.

    Use iter_descriptors() to yield.
    """

    def __init__(self, directories: list = [], dict_descriptors: list = []):
        self.directories = directories
        self.dict_descriptors = dict_descriptors

    def iter_descriptors(self):
        files = DescriptorsFromDirectory(self.directories).iter_files()
        yield from files

        for descriptor in self.dict_descriptors:
            yield Descriptor(descriptor)


class DescriptorsFromDirectory():
    """
    Helper class that handles yielding descriptors from a directory.

    Use iter_files() to yield Descriptor objects.
    """

    def __init__(self, directories: list):
        self.directories = directories

    def iter_files(self):
        yield from self._get_from_dir()

    def _get_from_dir(self):
        for directory in self.directories:
            self._check_if_path_exists(directory)
            for file_name in self._get_files_from_dir(directory):
                try:
                    yield DescriptorFromFile(directory, file_name).get_descriptor_obj()
                except (Exception, ValueError, RuntimeError) as e:
                    logger.error(e)
                    continue

    def _check_if_path_exists(self, dir_path):
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            raise RuntimeError(
                f"Unable to locate schema directory '{dir_path}'")

    def _get_files_from_dir(self, directory):
        yield from sorted([f for f in os.listdir(directory) if f.endswith('.json')])


class DescriptorFromFile():
    """
    Helper class that handles creating a descriptor when given a file path.
    """

    def __init__(self, schema_dir: str, file_name: str):
        self._check_if_the_file_is_a_directory(schema_dir, file_name)
        self.descriptor_obj = self._create_descriptor(schema_dir, file_name)

    def get_descriptor_obj(self):
        return self.descriptor_obj

    def _check_if_the_file_is_a_directory(
            self, schema_dir: str, file_name: str):
        if os.path.isdir(os.path.join(schema_dir, file_name)):
            raise RuntimeError(
                f"Cannot open a directory '{file_name}' as a descriptor.")

    def _create_descriptor(self, schema_dir: str, file_name: str):
        try:
            with open(os.path.join(schema_dir, file_name), 'r') as fh:
                try:
                    descriptor_dict = json.load(fh)
                except ValueError:
                    logger.info(
                        f"Failed to load JSON file. JSON is probably invalid in file '{os.path.join(schema_dir, file_name)}'")

        except Exception:
            raise RuntimeError(f"Error opening schema {file_name}")

        return Descriptor(descriptor_dict, file_name)


class Descriptor():
    """
    Stores all of the procedures for extracting data from descriptors.
    """
    def __init__(self, descriptor: dict, file_name: str = ""):
        self._descriptor = descriptor
        self._set_file_name(file_name, self.table_name)

    @property
    def table_name(self):
        try:
            return self._descriptor['datastore']['tablename']
        except KeyError:
            raise RuntimeError(
                "Error finding data in descriptor. Descriptor file may not be valid.")

    @property
    def table_schema(self):
        try:
            return self._descriptor['datastore']['schema']
        except KeyError:
            raise RuntimeError(
                "Error finding data in descriptor. Descriptor file may not be valid.")

    @property
    def api_schema(self):
        try:
            return self._descriptor['api']['methods'][0]
        except KeyError:
            raise RuntimeError(
                "Error finding data in descriptor. Descriptor file may not be valid.")

    @property
    def data_resource_name(self):
        try:
            return self._descriptor['api']['resource']
        except KeyError:
            raise RuntimeError(
                "Error finding data in descriptor. Descriptor file may not be valid.")

    @property
    def restricted_fields(self):
        try:
            return self._descriptor['datastore']['restricted_fields']
        except KeyError:
            return []

    @property
    def descriptor(self):
        return self._descriptor

    @property
    def file_name(self):
        return self._file_name

    def get_checksum(self) -> str:
        model_checksum = md5(
            json.dumps(
                self.table_schema,
                sort_keys=True
            ).encode('utf-8')
        ).hexdigest()

        return model_checksum

    def _set_file_name(self, file_name: str, table_name: str):
        if file_name == "":
            self._file_name = f"{table_name}.json"
        else:
            self._file_name = file_name
