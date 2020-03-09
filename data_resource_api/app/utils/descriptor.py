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
            raise RunTimeError(
                f"Unable to locate schema directory '{dir_path}'")

    def _get_file_from_dir(self, directory):
        lol = sorted([f for f in os.listdir(directory) if f.endswith('.json')])
        yield from lol


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
                except ValueError as e:
                    logger.info(
                        f"JSON is probably invalid in file '{os.path.join(schema_dir, file_name)}'")
                    logger.error(e)

        except Exception as e:
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
        # add validation checker here

        try:
            self.table_name = descriptor['datastore']['tablename']
        except KeyError:
            raise RuntimeError(
                "Error finding data in descriptor. Descriptor file may not be valid.")

        try:
            self.table_schema = descriptor['datastore']['schema']
        except KeyError:
            raise RuntimeError(
                "Error finding data in descriptor. Descriptor file may not be valid.")

        try:
            self.api_schema = descriptor['api']['methods'][0]
        except KeyError:
            raise RuntimeError(
                "Error finding data in descriptor. Descriptor file may not be valid.")

        try:
            self.data_resource_name = descriptor['api']['resource']
        except KeyError:
            raise RuntimeError(
                "Error finding data in descriptor. Descriptor file may not be valid.")

        try:
            self.restricted_fields = descriptor['datastore']['restricted_fields']
        except KeyError:
            self.restricted_fields = []

        try:
            self.descriptor = descriptor
        except KeyError:
            raise RuntimeError(
                "Error finding data in descritpor. Descriptor file may not be valid.")

        self._set_file_name(file_name, self.table_name)

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
