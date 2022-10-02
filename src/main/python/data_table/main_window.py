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
    QStyle
)
from .new_data_table import NewDataTableWidget
from .data_table import DataTable
from .data_table_actions_list_widget import DataTableActionsList
import logging

logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s %(lineno)s]')

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
        self.new_data_table_action=None
        self.initializeUI()

    def refresh_data_table_configs(self):
        self.data_table_configs = get_data_table_configs(
            pathlib.Path(
                self.appctxt.get_resource("data_tables/data_table_definitions")
            )
        )
        logging.debug("refreshed data table configs")

    def initializeUI(self):
        self.setGeometry(100, 100, 800, 700)
        self.setWindowTitle("Data Tables")
        self.menu_bar = self.menuBar()
        self.stacked_widget = QStackedWidget()
        self.new_data_table_widget = NewDataTableWidget(self, self.appctxt)
        self.stacked_widget.addWidget(self.new_data_table_widget)        
        self.initializeDataTables()
        self.create_file_menu()
        self.create_data_table_menu()
        self.initialize_data_config_actions_widget()
        self.add_new_data_table_to_file_menu()
        self.set_event_handler_of_new_data_table_action()
        self.add_data_config_actions_list_to_file_menu()
        self.setCentralWidget(self.stacked_widget)
        self.show()

    def initializeDataTables(self):
        self.data_table_widgets = {}
        for data_config in self.data_table_configs:
            self.add_new_data_table_to_stacked_widget(data_config)
    
    def create_file_menu(self):
        self.file_menu = self.menu_bar.addMenu("File")

    
    def create_data_table_menu(self):
        self.data_table_menu = self.menu_bar.addMenu("Data Table")
        self.populate_data_config_actions()


    def add_new_data_table_to_file_menu(self):
        self.new_data_table_action = QAction("New Data Table", self)
        self.new_data_table_action.setShortcut("Alt+N")
        icon = self.style().standardIcon(QStyle.SP_FileIcon)
        self.new_data_table_action.setIcon(icon)
        self.file_menu.addAction(self.new_data_table_action)
    
    def set_event_handler_of_new_data_table_action(self):
        self.new_data_table_action.triggered.connect(
            lambda x: self.stacked_widget.setCurrentWidget(self.new_data_table_widget)
        )

    def initialize_data_config_actions_widget(self):
        self.data_table_actions_list = DataTableActionsList(self, self.appctxt)

        self.stacked_widget.addWidget(
            self.data_table_actions_list.data_table_actions_window
        )
        self.stacked_widget.setCurrentWidget(
            self.data_table_actions_list.data_table_actions_window
        )
        logging.debug("finished adding data_config_actions_widget to stacked_widget")

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

    def add_data_config_actions_list_to_file_menu(self):
        action = QAction("Data Table Configs", self)
        action.setShortcut("Alt+L")
        icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        action.setIcon(icon)
        self.file_menu.addAction(action)

        def actions_list_selected():
            self.data_table_actions_list.data_table_actions_window.search_actions_le.clear()
            self.stacked_widget.setCurrentWidget(
                self.data_table_actions_list.data_table_actions_window
            )
            self.data_table_actions_list.data_table_actions_window.search_actions_le.setFocus()

        action.triggered.connect(actions_list_selected)

    def populate_data_config_actions(self):
        action_names = [act.text() for act in self.data_table_menu.actions()]
        self.data_config_actions={}
        for data_config in self.data_table_configs:
            self.data_config_actions[data_config["data_table_name"]] = QAction(
                data_config["data_table_full_name"], self
            )
            self.data_config_actions[data_config["data_table_name"]].triggered.connect(
                partial(self.data_config_selected, data_config)
            )
            logging.debug(f"will create action with name {data_config['data_table_name']}")
            action = self.data_config_actions[data_config["data_table_name"]]
            
            logging.debug(f"existing actions in data_table_menu : {action_names}")
            if action.text() not in action_names:
                self.data_table_menu.addAction(action)
                self.add_new_data_table_to_stacked_widget(data_config)
        
    
    def refresh_data_config_actions(self):
        self.data_config_actions={}
        self.populate_data_config_actions()
        

    def data_config_selected(self, data_config):
        logging.debug(self)
        logging.debug(data_config)
        self.stacked_widget.setCurrentWidget(
            self.data_table_widgets[data_config["data_table_name"]].data_table_window
        )
