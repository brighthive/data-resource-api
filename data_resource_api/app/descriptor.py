import os
import json


class DescriptorsGetter():
    """
    Given a list of directories and a list of descriptor files this
    class will handle the file loading and yielding of each descriptor.
    This greatly simplifies the code in the DMM.

    iter_descriptors yields a Descriptor object
    """
    def __init__(self, directories: list = [], custom_descriptors: list = []):
        # print(directories)
        self.directories = directories

    def iter_descriptors(self):
        yield from self._get_from_dir()

    def _get_from_dir(self):
        for directory in self.directories:
            self._check_if_path_exists(directory)
            for file_name in self._get_file_from_dir(directory):
                yield DescriptorFromFile(directory, file_name).get_descriptor_obj()

    def _check_if_path_exists(self, dir_path):
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            raise RunTimeError(f"Unable to locate schema directory '{dir_path}'")

    def _get_file_from_dir(self, directory):
        yield from [f for f in os.listdir(directory) if f.endswith('.json')]





class DescriptorFileHelper():
    def __init__(self, dir_path: str):
        self.check_if_path_exists(dir_path)
        self.get_only_json_files(dir_path)

    # def check_if_path_exists(self, dir_path):
    #     if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
    #         raise RunTimeError(f"Unable to locate schema directory '{dir_path}'")

    
    # # def get_only_json_files(self, dir_path):
    #     # self.schemas = [f for f in os.listdir(dir_path) if f.endswith('.json')]



class DescriptorFromFile():
    def __init__(self, schema_dir: str, file_name: str):
        self.check_if_the_file_is_a_directory(schema_dir, file_name)
        self.descriptor_obj = self.create_descriptor(schema_dir, file_name)

    def check_if_the_file_is_a_directory(self, schema_dir: str, file_name: str):
        if os.path.isdir(os.path.join(schema_dir, file_name)):
            raise RuntimeError(f"Cannot open a directory '{file_name}' as a descriptor.")

    def create_descriptor(self, schema_dir: str, file_name: str):
        self.descriptor_obj = {}
        # Open the file and store its json data and file name
        try:
            with open(os.path.join(schema_dir, file_name), 'r') as fh:
                try:
                    schema_dict = json.load(fh)
                except Exception as e:
                    raise e
        except Exception as e:
            raise RuntimeError(f"Error opening schema {file_name}")

        return Descriptor(schema_dict, file_name)

    def get_descriptor_obj(self):
        return self.descriptor_obj


class Descriptor():
    """
    This is a utility class to encapsulate functions and operations
    related to descriptor files.
    """
    def __init__(self, descriptor: dict, file_name: str = ""):
        try:
            self.table_name = descriptor['datastore']['tablename']
        except KeyError:
            raise RuntimeError("Error finding data in descritpor. Descriptor file may not be valid.")

        try:
            self.table_schema = descriptor['datastore']['schema']
        except KeyError:
            raise RuntimeError("Error finding data in descritpor. Descriptor file may not be valid.")

        try:
            self.api_schema = descriptor['api']['methods'][0]
        except KeyError:
            raise RuntimeError("Error finding data in descritpor. Descriptor file may not be valid.")

        try:
            self.data_resource_name = descriptor['api']['resource']
        except KeyError:
            raise RuntimeError("Error finding data in descritpor. Descriptor file may not be valid.")

        try:
            self.descriptor = descriptor
        except KeyError:
            raise RuntimeError("Error finding data in descritpor. Descriptor file may not be valid.")

        # self.file_name = self._set_file_name(file_name, self.table_name)
        self.file_name = file_name

    # def _set_file_name(self, file_name: str, table_name: str):
    #     if file_name is None:
    #         self.file_name = f"{table_name}.json"
    #     else:
    #         self.file_name = file_name
