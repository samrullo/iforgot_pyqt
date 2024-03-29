import os
from typing import List
import pathlib
import json
from PyQt5.QtWidgets import (
    QWidget,
    QFormLayout,
    QPushButton,
    QMessageBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt5.QtGui import QFont

from utils.my_pyqt_utils import deleteItemsOfLayout
from .config import CSSConfig
import logging
from .bulk_data_upload import BulkUpload

from abc import ABCMeta,abstractmethod

class ABCNewDataTable(metaclass=ABCMeta):
    @abstractmethod
    def create_new_data_table_config(table_full_name:str,columns:List,config_filepath:pathlib.Path):
        """
        Create new data table config based on user input
        such as table name, number of columns and
        """
        pass




class NewDataTableWidget(QWidget):
    def __init__(self, main_window, appctxt) -> None:
        super().__init__()
        self.main_window = main_window
        self.appctxt = appctxt
        self.initializeUI()

    def initializeUI(self):
        self.setGeometry(100, 100, 800, 700)
        self.setWindowTitle("New Data Table")
        self.form_layout = QFormLayout()

        data_table_name_lbl = QLabel("Data Table Name")

        self.data_table_name_le = QLineEdit()

        no_of_cols_lbl = QLabel("Number of columns")

        self.no_of_cols_le = QLineEdit()

        no_of_cols_btn = QPushButton("Populate form")
        no_of_cols_btn.setObjectName(CSSConfig.GREEN_BIG_BUTTON)
        no_of_cols_btn.clicked.connect(self.populate_columns_name_fields)

        bulk_upload_btn = QPushButton("Bulk Upload")
        bulk_upload_btn.setObjectName(CSSConfig.GREEN_BIG_BUTTON)
        bulk_upload_btn.clicked.connect(self.bulk_upload)

        dt_form_layout = QFormLayout()
        dt_form_layout.addRow(data_table_name_lbl, self.data_table_name_le)
        dt_form_layout.addRow(no_of_cols_lbl, self.no_of_cols_le)
        dt_form_layout.addRow(no_of_cols_btn)
        dt_form_layout.addRow(bulk_upload_btn)

        v_box = QVBoxLayout()
        v_box.addLayout(dt_form_layout)
        self.col_form_layout = QFormLayout()
        v_box.addLayout(self.col_form_layout)
        self.v_box = v_box

        self.setLayout(v_box)
        self.show()

    def populate_columns_name_fields(self):
        answer = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to populate columns name fields?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            deleteItemsOfLayout(self.col_form_layout)

            self.column_names = []
            try:
                no_of_cols = int(self.no_of_cols_le.text())
                for i in range(no_of_cols):
                    _col_lbl = QLabel("Column {}".format(i + 1))

                    _col_le = QLineEdit()

                    self.column_names.append(_col_le)
                    self.col_form_layout.addRow(_col_lbl, _col_le)
                submit_btn = QPushButton("Submit")
                submit_btn.setObjectName(CSSConfig.GREEN_BIG_BUTTON)
                submit_btn.clicked.connect(self.submit_columns_name_fields)
                self.col_form_layout.addRow(submit_btn)
            except:
                QMessageBox.warning(self, "Error", "Please enter a valid number")
        else:
            pass

    def submit_columns_name_fields(self):
        data_table_def = {
            "data_table_name": self.data_table_name_le.text().lower().replace(" ", "_"),
            "data_table_full_name": self.data_table_name_le.text(),
            "no_cols": self.no_of_cols_le.text(),
            "column_names": [col_le.text() for col_le in self.column_names],
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

        # next generate empty file in data_table_contents folder
        data_table_contents_folder = pathlib.Path(
            self.appctxt.get_resource("data_tables/data_table_contents")
        )
        data_table_contents_file = data_table_contents_folder / (
            data_table_def["data_table_name"] + ".json"
        )
        with open(data_table_contents_file, "w") as f:
            json.dump([{}], f)

        # next add new data table to main window menu
        self.main_window.refresh_data_table_configs()        
        self.main_window.populate_data_config_actions()

        QMessageBox.information(self, "Successfully saved", "Successfully saved")
        for col_le in self.column_names:
            logging.debug(col_le.text())
        deleteItemsOfLayout(self.col_form_layout)
        
        # clear data table name and no of cols LineEdit widgets
        self.data_table_name_le.clear()
        self.no_of_cols_le.clear()
        
        # add newly added data to data table actions list and move to data table actions list widget
        self.main_window.data_table_actions_list.populate_data_table_actions_list()
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.data_table_actions_list.data_table_actions_window
        )

    def bulk_upload(self):
        bu_obj=BulkUpload(self.main_window,self.appctxt)
        bu_obj.choose_bulk_upload_file()
        bu_obj.create_data_table_config_and_bulk_upload_data()

        # next add new data table to main window menu
        self.main_window.refresh_data_table_configs()        
        self.main_window.populate_data_config_actions()
        
        # add newly added data to data table actions list and move to data table actions list widget
        self.main_window.data_table_actions_list.populate_data_table_actions_list()
        self.main_window.stacked_widget.setCurrentWidget(
            self.main_window.data_table_actions_list.data_table_actions_window
        )