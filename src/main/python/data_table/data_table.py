import os
import re
import pathlib
import json
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QMessageBox,
)

from PyQt5.QtCore import Qt
import logging
import shutil

from abc import ABCMeta, abstractmethod

from utils.data_table_utils import back_up_data_file
from .config import CSSConfig
from utils.data_table_utils import (
    get_column_name_from_qtable_item,
    get_key_column_value_from_qtable_item,
    get_data_table_content_value_from_key,
)


class ABCDataTable(metaclass=ABCMeta):
    @abstractmethod
    def read_data_table_contents():
        """
        This method will read data table contents from
        a path where they are stored
        """
        pass

    @abstractmethod
    def filter_data():
        """
        This method will filter data table widget rows
        based on what user enters in the search QLineEdit widget
        """
        pass

    @abstractmethod
    def add_data():
        """
        Add new data into data table
        """
        pass

    @abstractmethod
    def update():
        """
        Update existing data in data table
        This is done by editing QTableWidgetItems directly
        """
        pass

    @abstractmethod
    def delete():
        """
        Delete data from data table
        This is done by highlighting certain row of QTableWidget
         and then pressing delete button
        """
        pass


class DataTableWindow(QWidget):
    def __init__(self, data_config) -> None:
        super().__init__()
        self.data_config = data_config

    def initializeUI(self):
        self.setGeometry(100, 100, 800, 700)
        self.form_layout = QHBoxLayout()
        self.v_box = QVBoxLayout()
        self.data_table_widget = QTableWidget()

        title = QLabel(self.data_config["data_table_full_name"])
        title.setAlignment(Qt.AlignCenter)

        # search section
        search_label = QLabel("Search text")
        search_le = QLineEdit()
        self.search_le = search_le
        search_col_lbl = QLabel("Search column")
        search_col = QComboBox()
        search_col.addItems([col for col in self.data_config["column_names"]])
        self.search_col = search_col
        form_layout = QFormLayout()
        form_layout.addRow(search_label, search_le)
        form_layout.addRow(search_col_lbl, search_col)

        self.v_box.addWidget(title)
        self.v_box.addLayout(form_layout)
        self.v_box.addWidget(self.data_table_widget)

        # add button to add new data table content
        self.new_data_table_content_btn = QPushButton("New Data")
        self.new_data_table_content_btn.setObjectName(CSSConfig.GREEN_BIG_BUTTON)
        self.v_box.addWidget(self.new_data_table_content_btn)

        # add button to delete data from data table
        self.delete_data_table_content_btn = QPushButton("Delete Data")
        self.delete_data_table_content_btn.setObjectName(CSSConfig.GREEN_BIG_BUTTON)
        self.v_box.addWidget(self.delete_data_table_content_btn)

        self.setLayout(self.v_box)

    def populate_table_widget_data(self, data_table_contents):
        table_columns = self.data_config["column_names"]
        tableWidgetColumnsDict = {col: i for i, col in enumerate(table_columns)}
        self.data_table_widget.setColumnCount(len(tableWidgetColumnsDict))
        self.data_table_widget.setRowCount(len(data_table_contents))

        # set table column names
        self.data_table_widget.setHorizontalHeaderLabels(
            [col.upper() for col in tableWidgetColumnsDict.keys()]
        )

        for row_idx, data_table_content in enumerate(data_table_contents):
            if len(data_table_content) != 0:
                for col in tableWidgetColumnsDict:
                    item = QTableWidgetItem(data_table_content[col])
                    self.data_table_widget.setItem(
                        row_idx, tableWidgetColumnsDict[col], item
                    )
                    if tableWidgetColumnsDict[col] == 0:
                        item.setFlags((item.flags()) & (~Qt.ItemIsEditable))


class NewDataTableContentWindow(QWidget):
    def __init__(self, data_config) -> None:
        super().__init__()
        self.data_config = data_config

    def initializeUI(self):
        v_box = QVBoxLayout()
        form_layout = QFormLayout()
        columns = self.data_config["column_names"]
        column_line_edits_dict = {}
        for column in columns:
            col_label = QLabel(column)
            col_le = QLineEdit()
            column_line_edits_dict[column] = col_le
            form_layout.addRow(col_label, col_le)
        self.column_line_edits_dict = column_line_edits_dict
        self.add_btn = QPushButton("Add")
        self.add_btn.setObjectName(CSSConfig.GREEN_BIG_BUTTON)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName(CSSConfig.GREEN_BIG_BUTTON)
        v_box.addWidget(
            QLabel(f"New content for {self.data_config['data_table_full_name']}")
        )
        v_box.addLayout(form_layout)
        v_box.addWidget(self.add_btn)
        v_box.addWidget(self.cancel_btn)
        self.setLayout(v_box)


class DataTable(ABCDataTable):
    def __init__(self, data_config, appctxt, stacked_widget_layout) -> None:
        super().__init__()
        self.appctxt = appctxt
        self.data_config = data_config
        self.stacked_widget_layout = stacked_widget_layout
        self.data_table_window = DataTableWindow(self.data_config)
        self.new_data_table_content_window = NewDataTableContentWindow(self.data_config)
        self.data_table_contents_folder = self.appctxt.get_resource(
            "data_tables/data_table_contents"
        )

        self.data_table_name = self.data_config["data_table_name"]
        self.data_table_full_name = self.data_config["data_table_full_name"]
        self.data_table_path = pathlib.Path(self.data_table_contents_folder) / (
            self.data_table_name + ".json"
        )
        if not self.data_table_path.exists():
            with open(self.data_table_path, "w") as f:
                json.dump([{}], f)
        self.data_table_contents = self.read_data_table_contents()

        # initialize DataTableWindow widget with all its UI elements
        self.data_table_window.initializeUI()
        self.data_table_window.populate_table_widget_data(self.data_table_contents)
        self.new_data_table_content_window.initializeUI()

        # set event handlers
        self.set_event_handlers()

    def set_event_handlers(self):
        # set event handler for filtering data table contents
        self.data_table_window.search_le.textChanged.connect(self.filter_data)

        # set event handler to view QWidget with QForm layout for adding new data
        self.data_table_window.new_data_table_content_btn.clicked.connect(
            lambda x: self.stacked_widget_layout.setCurrentWidget(
                self.new_data_table_content_window
            )
        )

        # event handler to add new data table content
        self.new_data_table_content_window.add_btn.clicked.connect(self.add_data)

        # will use this flag to identify if the cell can be passed for itemChanged
        # set event handler to flip the flag when QTableWidgetItem is double clicked
        self.item_double_clicked_flag = False
        self.data_table_window.data_table_widget.itemDoubleClicked.connect(
            self.item_double_clicked
        )

        # self event handler to change data table content
        # The application will update data only when double clicked flag is True
        self.data_table_window.data_table_widget.itemChanged.connect(self.update)

        # set event handler to delete data table content
        self.data_table_window.delete_data_table_content_btn.clicked.connect(
            self.delete
        )

    def item_double_clicked(self, item):
        print("will set double clicked flag to true")
        self.item_double_clicked_flag = True

    def read_data_table_contents(self):
        with open(self.data_table_path, "r") as f:
            data_table_contents = json.load(f)
        return data_table_contents

    def filter_data(self):
        filter_by = self.data_table_window.search_col.currentText()
        search_txt = self.data_table_window.search_le.text().lower()
        filtered_data_list = [
            data_item
            for data_item in self.data_table_contents
            if search_txt.lower() in data_item[filter_by].lower()
        ]
        self.data_table_window.data_table_widget.clear()
        self.data_table_window.populate_table_widget_data(filtered_data_list)

    def add_data(self):
        print(
            f"will add {[(col,val.text()) for col,val in self.new_data_table_content_window.column_line_edits_dict.items()]}"
        )
        answer = QMessageBox.question(
            self.new_data_table_content_window,
            "Confirm",
            "Are you sure you want to add new data?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if answer == QMessageBox.Yes:
            self.data_table_contents.append(
                {
                    col: val.text()
                    for col, val in self.new_data_table_content_window.column_line_edits_dict.items()
                }
            )
            back_up_data_file(self.data_table_path, bkup_no=5)
            with open(self.data_table_path, "w") as fh:
                json.dump(self.data_table_contents, fh)
            self.stacked_widget_layout.setCurrentWidget(self.data_table_window)

    def update(self, item: QTableWidgetItem):
        if self.item_double_clicked_flag:
            print("Implement DataTable update method")
            print(f"item row: {item.row()}, item column : {item.column()}")
            print(f"item text : {item.text()}, item value : {item.data(0)}")
            key_column_val = get_key_column_value_from_qtable_item(
                item, self.data_table_window.data_table_widget
            )
            key_column_name = get_column_name_from_qtable_item(
                self.data_table_window.data_table_widget.item(item.row(), 0),
                self.data_config["column_names"],
            )
            column_name = get_column_name_from_qtable_item(
                item, self.data_config["column_names"]
            )
            current_item_val = get_data_table_content_value_from_key(
                self.data_table_contents, key_column_name, key_column_val, column_name
            )
            print(
                f"Change data table widget item from {current_item_val} to {item.data(0)}"
            )
            answer = QMessageBox.question(
                self.data_table_window,
                "Confirm",
                f"Are you sure you want to change from {current_item_val} to {item.text()}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if answer == QMessageBox.Yes:
                for data_table_content in self.data_table_contents:
                    if data_table_content[key_column_name] == key_column_val:
                        data_table_content[column_name] = item.text()
                        break
                back_up_data_file(self.data_table_path, bkup_no=5)
                with open(self.data_table_path, "w") as fh:
                    json.dump(self.data_table_contents, fh)
            self.item_double_clicked_flag = False
        else:
            print("item_double_clicked flag was False so will not do anything")

    def delete(self):
        item=self.data_table_window.data_table_widget.currentItem()
        print("Implement DataTable delete method", item)
