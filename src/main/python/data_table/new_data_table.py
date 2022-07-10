import os
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

        dt_form_layout = QFormLayout()
        dt_form_layout.addRow(data_table_name_lbl, self.data_table_name_le)
        dt_form_layout.addRow(no_of_cols_lbl, self.no_of_cols_le)
        dt_form_layout.addRow(no_of_cols_btn)

        v_box = QVBoxLayout()
        v_box.addLayout(dt_form_layout)
        self.col_form_layout = QFormLayout()
        v_box.addLayout(self.col_form_layout)
        self.v_box = v_box

        self.setLayout(v_box)
        self.show()

    def boxdelete(self, box):
        for i in range(self.vlayout.count()):
            layout_item = self.vlayout.itemAt(i)
            if layout_item.layout() == box:
                deleteItemsOfLayout(layout_item.layout())
                self.vlayout.removeItem(layout_item)
                break

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
        print(f"attempting to save {data_table_def} into {data_table_def_file}")
        with open(data_table_def_file, "w") as f:
            json.dump(data_table_def, f)
        print(f"saved data_table def into {data_table_def_file}")

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
            print(col_le.text())
        deleteItemsOfLayout(self.col_form_layout)
