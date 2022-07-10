from PyQt5.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
)

from utils.data_table_utils import find_data_config_from_name
from abc import ABC, ABCMeta, abstractclassmethod, abstractmethod


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
        data_config_actions_list_widget = QListWidget()
        # search box
        form_layout = QFormLayout()
        search_actions_le = QLineEdit()
        form_layout.addRow(QLabel("Search"), search_actions_le)

        data_config_actions_vb = QVBoxLayout()
        data_config_actions_vb.addLayout(form_layout)
        data_config_actions_vb.addWidget(data_config_actions_list_widget)
        self.data_config_actions_list_widget = data_config_actions_list_widget
        self.search_actions_le = search_actions_le

        self.setLayout(data_config_actions_vb)

    def keyPressEvent(self, event):
        print(f"you pressed {event.key()}")


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

    def item_double_clicked(self, list_widget_item):
        action_name = list_widget_item.text()
        print(f"will try to find data_config from {action_name}")
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

    def search_data_table_actions(self, text):
        self.data_table_actions_window.data_config_actions_list_widget.clear()
        for action_name in self.main_window.data_config_actions.keys():
            if text in action_name:
                self.data_table_actions_window.data_config_actions_list_widget.addItem(
                    action_name
                )

    def remove_data_table(self):
        print("Implement remove data table function")
