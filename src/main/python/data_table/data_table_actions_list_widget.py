from PyQt5.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QToolButton
)
import os
import pathlib
import shutil
from utils.data_table_utils import find_data_config_from_name
from abc import ABC, ABCMeta, abstractclassmethod, abstractmethod
from .config import CSSConfig
import logging

class ABCDataTableActionsList(metaclass=ABCMeta):
    @abstractmethod
    def populate_data_table_actions_list():
        pass

    @abstractclassmethod
    def search_data_table_actions():
        pass

    @abstractclassmethod
    def remove_data_table():
        pass


class DataTableActionsListWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

    def initializeUI(self):
        # QListWidget will contain list of data config actions which are used to access
        # individual data tables by double clicking on QListWidget item
        data_config_actions_list_widget = QListWidget()
        # search box
        form_layout = QFormLayout()
        search_actions_le = QLineEdit()
        form_layout.addRow(QLabel("Search"), search_actions_le)

        data_config_actions_vb = QVBoxLayout()
        data_config_actions_vb.addLayout(form_layout)
        data_config_actions_vb.addWidget(data_config_actions_list_widget)

        # add two buttons to add new data table definition or to remove a data table alltogether
        new_data_config_btn=QPushButton("New Data Config")
        new_data_config_btn.setObjectName(CSSConfig.GREEN_BIG_BUTTON)

        delete_data_config_btn = QPushButton("Delete Data Config")
        delete_data_config_btn.setObjectName(CSSConfig.GREEN_BIG_BUTTON)

        # set widgets as member variables for later use
        self.data_config_actions_list_widget = data_config_actions_list_widget
        self.search_actions_le = search_actions_le
        self.new_data_config_btn = new_data_config_btn
        self.delete_data_config_btn = delete_data_config_btn

        data_config_actions_vb.addWidget(self.new_data_config_btn)
        data_config_actions_vb.addWidget(self.delete_data_config_btn)

        self.setLayout(data_config_actions_vb)

    def keyPressEvent(self, event):
        logging.debug(f"you pressed {event.key()}")


class DataTableActionsList(ABCDataTableActionsList):
    def __init__(self, main_window, appctxt) -> None:
        super().__init__()
        self.main_window = main_window
        self.appctxt = appctxt
        self.data_table_actions_window = DataTableActionsListWindow()
        self.data_table_actions_window.initializeUI()
        self.populate_data_table_actions_list()
        self.data_table_actions_window.search_actions_le.textChanged.connect(
            self.search_data_table_actions
        )

        self.data_table_actions_window.data_config_actions_list_widget.itemDoubleClicked.connect(
            self.item_double_clicked
        )

        self.data_table_actions_window.new_data_config_btn.clicked.connect(lambda x: self.main_window.stacked_widget.setCurrentWidget(self.main_window.new_data_table_widget))
        self.data_table_actions_window.delete_data_config_btn.clicked.connect(self.remove_data_table)

    def item_double_clicked(self, list_widget_item):
        action_name = list_widget_item.text()
        logging.debug(f"will try to find data_config from {action_name}")
        data_config = find_data_config_from_name(
            self.main_window.data_table_configs, action_name
        )
        self.main_window.data_config_selected(data_config)

    def populate_data_table_actions_list(self):
        self.data_table_actions_window.data_config_actions_list_widget.clear()
        for action_name in self.main_window.data_config_actions.keys():
            self.data_table_actions_window.data_config_actions_list_widget.addItem(
                action_name
            )
        logging.debug("completed populate data table actions list")

    def search_data_table_actions(self, text):
        self.data_table_actions_window.data_config_actions_list_widget.clear()
        for action_name in self.main_window.data_config_actions.keys():
            if text in action_name:
                self.data_table_actions_window.data_config_actions_list_widget.addItem(
                    action_name
                )

    def remove_data_table(self):
        item = self.data_table_actions_window.data_config_actions_list_widget.currentItem()
        logging.debug(f"Remove data table {item.text()}")
        dtd_folder=pathlib.Path(self.appctxt.get_resource("data_tables/data_table_definitions"))
        dtd_bkup_folder=dtd_folder/"bkup"
        if not dtd_bkup_folder.exists():
            os.makedirs(dtd_bkup_folder)
        dtd_filename=item.text()+".json"
        shutil.move(dtd_folder/dtd_filename,dtd_bkup_folder/dtd_filename)
        logging.debug(f"moved {dtd_filename} from {dtd_folder} to {dtd_bkup_folder} ")
        self.main_window.refresh_data_table_configs()
        self.main_window.populate_data_config_actions()
        self.populate_data_table_actions_list()       

