from utils.data_table_utils import get_data_table_configs, find_data_config_from_name
import pathlib
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
    QToolButton,
    QListWidget,
    QFormLayout,
    QLineEdit,
    QLabel,
)
from .new_data_table import NewDataTableWidget
from .data_table import DataTable
from .data_table_actions_list_widget import DataTableActionsList


class MainWindow(QMainWindow):
    def __init__(self, appctxt):
        super().__init__()
        self.appctxt = appctxt
        self.data_table_configs = get_data_table_configs(
            pathlib.Path(
                self.appctxt.get_resource("data_tables/data_table_definitions")
            )
        )
        self.data_config_actions = {}
        self.initializeUI()

    def refresh_data_table_configs(self):
        self.data_table_configs = get_data_table_configs(
            pathlib.Path(
                self.appctxt.get_resource("data_tables/data_table_definitions")
            )
        )

    def initializeUI(self):
        self.setGeometry(100, 100, 800, 700)
        self.setWindowTitle("Data Tables")
        self.menu_bar = self.menuBar()
        self.stacked_widget = QStackedWidget()
        self.new_data_table_widget = NewDataTableWidget(self, self.appctxt)
        self.stacked_widget.addWidget(self.new_data_table_widget)
        self.data_config_actions_vb = None
        self.initializeDataTables()
        self.create_file_menu()
        self.create_data_table_menu()
        self.initialize_data_config_actions_widget()
        self.add_new_data_table_to_file_menu()
        self.add_data_config_actions_list_to_file_menu()
        self.setCentralWidget(self.stacked_widget)
        self.show()

    def initialize_data_config_actions_widget(self):
        self.data_table_actions_list = DataTableActionsList(self, self.appctxt)

        self.stacked_widget.addWidget(
            self.data_table_actions_list.data_table_actions_window
        )
        self.stacked_widget.setCurrentWidget(
            self.data_table_actions_list.data_table_actions_window
        )
        print("finished adding data_config_actions_widget to stacked_widget")

    def add_data_config_action_to_vb(self, data_config_action):
        btn = QToolButton()
        btn.setDefaultAction(data_config_action)
        self.data_config_actions_vb.addWidget(btn)

    def initializeDataTables(self):
        self.data_table_widgets = {}
        for data_config in self.data_table_configs:
            self.add_new_data_table_to_stacked_widget(data_config)

    def add_new_data_table_to_stacked_widget(self, data_config):
        self.data_table_widgets[data_config["data_table_name"]] = DataTable(
            data_config, self.appctxt, self.stacked_widget
        )
        self.stacked_widget.addWidget(
            self.data_table_widgets[data_config["data_table_name"]].data_table_window
        )
        self.stacked_widget.addWidget(
            self.data_table_widgets[
                data_config["data_table_name"]
            ].new_data_table_content_window
        )

    def create_file_menu(self):
        self.file_menu = self.menu_bar.addMenu("File")

    def add_new_data_table_to_file_menu(self):
        new_data_table_action = QAction("New Data Table", self)
        self.file_menu.addAction(new_data_table_action)
        new_data_table_action.triggered.connect(
            lambda x: self.stacked_widget.setCurrentWidget(self.new_data_table_widget)
        )

    def add_data_config_actions_list_to_file_menu(self):
        action = QAction("Data Table Configs", self)
        self.file_menu.addAction(action)

        def actions_list_selected():
            self.data_table_actions_list.data_table_actions_window.search_actions_le.clear()
            self.stacked_widget.setCurrentWidget(
                self.data_table_actions_list.data_table_actions_window
            )

        action.triggered.connect(actions_list_selected)

    def create_data_table_menu(self):
        self.data_table_menu = self.menu_bar.addMenu("Data Table")
        self.populate_data_config_actions()

    def populate_data_config_actions(self):
        for data_config in self.data_table_configs:
            self.data_config_actions[data_config["data_table_name"]] = QAction(
                data_config["data_table_full_name"], self
            )
            self.data_config_actions[data_config["data_table_name"]].triggered.connect(
                partial(self.data_config_selected, data_config)
            )
            print(f"will create action with name {data_config['data_table_name']}")
            action = self.data_config_actions[data_config["data_table_name"]]
            action_names = [act.text() for act in self.data_table_menu.actions()]
            print(f"existing actions in data_table_menu : {action_names}")
            if action.text() not in action_names:
                self.data_table_menu.addAction(action)
                self.add_new_data_table_to_stacked_widget(data_config)

    def data_config_selected(self, data_config):
        print(self)
        print(data_config)
        self.stacked_widget.setCurrentWidget(
            self.data_table_widgets[data_config["data_table_name"]].data_table_window
        )
