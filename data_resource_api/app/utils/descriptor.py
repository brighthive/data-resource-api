import os
import json
from data_resource_api.logging import LogFactory
from hashlib import md5

logger = LogFactory.get_console_logger('descriptor-utils')


class DescriptorsGetter():
    """
    Given a list of directories and a list of descriptor files this
    class will handle the file loading and yielding of each descriptor.
    This greatly simplifies the code in the DMM.

    iter_descriptors yields a Descriptor object
    """

    def __init__(self, directories: list = [], custom_descriptors: list = []):
        self.directories = directories
        self.custom_descriptors = custom_descriptors

    def iter_descriptors(self):
        files = DescriptorFileHelper(self.directories).iter_files()
        yield from files

        descriptors = DescriptorCustomHelper(
            self.custom_descriptors).iter_descriptors()
        yield from descriptors


class DescriptorFileHelper():
    """
    This class when given a list of directories will handle yielding them
    as Descriptor objects.
    """

    def __init__(self, directories: list):
        self.directories = directories

    def iter_files(self):
        yield from self._get_from_dir()

    def _get_from_dir(self):
        for directory in self.directories:
            self._check_if_path_exists(directory)
            for file_name in self._get_file_from_dir(directory):
                try:
                    yield DescriptorFromFile(directory, file_name).get_descriptor_obj()
                except (Exception, ValueError, RuntimeError) as e:
                    logger.error(e)
                    continue

    def _check_if_path_exists(self, dir_path):
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            raise RuntimeError(
                f"Unable to locate schema directory '{dir_path}'")

    def _get_file_from_dir(self, directory):
        yield from sorted([f for f in os.listdir(directory) if f.endswith('.json')])


class DescriptorFromFile():
    """
    This class takes a directory and file name and does logical checks on the file
    and then exposes a Descriptor object.
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


class DescriptorCustomHelper():
    """
    This class is intended to receieve a list of descriptor dictionaries
    and provides an interface to yield Descriptor objects from that list.
    """

    def __init__(self, descriptors: list):
        self.descriptors = descriptors

    def iter_descriptors(self):
        for descriptor in self.descriptors:
            yield Descriptor(descriptor)


class Descriptor():
    """
    This utility class encompasses frequent operations performed on
    descriptor dictionaries.

    It reduces code reuse!
    """
    def __init__(self, descriptor: dict, file_name: str = ""):
        self.descriptor = descriptor
        self._set_file_name(file_name, self.table_name)

    @property
    def table_name(self):
        try:
            self.table_name = self.descriptor['datastore']['tablename']
        except KeyError:
            raise RuntimeError(
                "Error finding data in descriptor. Descriptor file may not be valid.")

    @property
    def table_schema(self):
        try:
            self.table_schema = self.descriptor['datastore']['schema']
        except KeyError:
            raise RuntimeError(
                "Error finding data in descriptor. Descriptor file may not be valid.")

    @property
    def api_schema(self):
        try:
            self.api_schema = self.descriptor['api']['methods'][0]
        except KeyError:
            raise RuntimeError(
                "Error finding data in descriptor. Descriptor file may not be valid.")

    @property
    def data_resource_name(self):
        try:
            self.data_resource_name = self.descriptor['api']['resource']
        except KeyError:
            raise RuntimeError(
                "Error finding data in descriptor. Descriptor file may not be valid.")

    @property
    def restricted_fields(self):
        try:
            self.restricted_fields = self.descriptor['datastore']['restricted_fields']
        except KeyError:
            self.restricted_fields = []

    @property
    def descriptor(self):
        return self.descriptor

    def _set_file_name(self, file_name: str, table_name: str):
        if file_name == "":
            self.file_name = f"{table_name}.json"
        else:
            self.file_name = file_name

    def get_checksum(self) -> str:
        model_checksum = md5(
            json.dumps(
                self.table_schema,
                sort_keys=True
            ).encode('utf-8')
        ).hexdigest()

        return model_checksum
