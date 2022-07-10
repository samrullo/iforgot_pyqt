from PyQt5.QtWidgets import (
    QDialog,
    QTableWidgetItem,
    QDialogButtonBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QComboBox,
    QHeaderView,
)

import logging


class DataTableChangeDialog(QDialog):
    def __init__(self, data_table_widget, item: QTableWidgetItem):
        super().__init__()
        self.setWindowTitle("Data Change dialog")
        self.data_table_widget = data_table_widget
        self.item = item
        logging.info(f"I inherit info from data widget : {self.data_table_widget.filter_by}")

        Qbtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(Qbtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.client_name = self.find_data_key_column_name()
        self.item_key_name = self.find_key_name_by_column()
        self.item_new_value = self.item.text()
        self.item_current_value = self.get_data_current_value(
            self.client_name, self.item_key_name
        )

        layout = QVBoxLayout()
        layout.addWidget(
            QLabel(
                f"Do you want to update {self.item_key_name} value from {self.item_current_value} to {self.item_new_value}?"
            )
        )
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def accept(self):
        logging.info(f"intercepted accept signal")
        self.update_data(self.client_name, self.item_key_name, self.item_new_value)
        super().accept()

    def find_key_name_by_column(self):
        column_idx = self.item.column()
        matching_keys = [
            key
            for key, val in self.data_table_widget.tableWidgetColumnsDict.items()
            if val == column_idx
        ]
        if len(matching_keys) > 0:
            matching_key = matching_keys[0]
            return matching_key

    def find_data_key_column_name(self):
        row_idx = self.item.row()
        data_key_column_name = self.data_table_widget.tableWidget.item(row_idx, 0).text()
        logging.info(
            f"located data key column name : {data_key_column_name}, row_idx : {row_idx}"
        )
        return data_key_column_name

    def update_data(self, data_first_column_name, key_name, key_new_value):
        for data_item in self.data_table_widget.data_list:
            if data_item[self.data_table_widget.first_column_name] == data_first_column_name:
                data_item[key_name] = key_new_value
                break
        GenericDataManager.update_data(
            self.data_table_widget.data_list, self.data_table_widget.data_file
        )

    def get_data_current_value(self, data_first_column_name, key_name):
        for data_item in self.data_table_widget.data_list:
            if data_item[self.data_table_widget.first_column_name] == data_first_column_name:
                return data_item[key_name]
