from abc import ABCMeta,abstractmethod
import pathlib
from .data_table import DataTable
import json
from PyQt5.QtWidgets import QFileDialog
import logging

class ABCBulkUpload(metaclass=ABCMeta):
    @abstractmethod
    def choose_bulk_upload_file():
        # opens a Dialog Widged so that the user can navigate to the path where bulk upload file is stored
        # save the bulk upload file path in a member variable
        pass

    @abstractmethod
    def bulk_upload_data():
        # read data table records from bulk_upload_file and append them to existing data table contents
        # if the file is a list of json objects, then it is a matter of using json.load
        # and then combinining two lists, i.e. data_table.data_table_contents and bulk_upload_file_contents
        pass

class BulkUpload(ABCBulkUpload):
    def __init__(self,main_window,appctxt) -> None:
        super().__init__()
        self.appctxt=appctxt
        self.main_window = main_window
        self.bulk_upload_file = None
        self.data_table = None
    
    def choose_bulk_upload_file(self):
        bulk_upload_filename,selectedFilter=QFileDialog.getOpenFileName(self.main_window,"Open file","","JSON files (*.json)")
        logging.debug(f"Chose bulk upload file name : {bulk_upload_filename}")
        self.bulk_upload_file=pathlib.Path(bulk_upload_filename)

    def create_data_table_config_file(self,data_table_name,data_table_full_name,no_cols,columns):
        data_table_def = {
            "data_table_name": data_table_name,
            "data_table_full_name": data_table_full_name,
            "no_cols": no_cols,
            "column_names": columns,
        }
        data_table_def_folder = pathlib.Path(
            self.appctxt.get_resource("data_tables/data_table_definitions")
        )
        data_table_def_file = data_table_def_folder / (
            data_table_def["data_table_name"] + ".json"
        )
        logging.debug(f"attempting to save {data_table_def} into {data_table_def_file}")
        with open(data_table_def_file, "w") as f:
            json.dump(data_table_def, f)
        logging.debug(f"saved data_table def into {data_table_def_file}")

    def create_data_table_config_and_bulk_upload_data(self):
        data_table_name,data_table_full_name,no_cols,columns,file_json_contents=self.get_data_table_config_attributes_from_file()
        self.create_data_table_config_file(data_table_name,data_table_full_name,no_cols,columns)
        self.bulk_upload_data(data_table_name,file_json_contents)

    
    def get_data_table_config_attributes_from_file(self):
        data_table_name=self.bulk_upload_file.stem
        data_table_full_name=" ".join([token[0].upper()+token[1:] for token in data_table_name.split("_")])
        file_txt=self.bulk_upload_file.read_text()
        file_json_contents=json.loads(file_txt)
        file_json_single_content=file_json_contents[0]
        columns=list(file_json_single_content.keys())
        return data_table_name,data_table_full_name,len(columns),columns,file_json_contents

    def bulk_upload_data(self,data_table_name,file_json_contents):
        # next generate empty file in data_table_contents folder
        data_table_contents_folder = pathlib.Path(
            self.appctxt.get_resource("data_tables/data_table_contents")
        )
        data_table_contents_file = data_table_contents_folder / (f"{data_table_name}.json")
        with open(data_table_contents_file, "w") as f:
            json.dump(file_json_contents, f)