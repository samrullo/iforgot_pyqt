import os
import re
import pathlib
import json
import shutil
import logging


def read_data_table_config(data_table_config_file_path: pathlib.Path):
    if not data_table_config_file_path.exists():
        return None
    with open(data_table_config_file_path, "r") as f:
        data_table_config = json.load(f)
    return data_table_config


def get_data_table_configs(data_table_config_folder_path: pathlib.Path):
    data_table_configs = []
    for data_table_config_file_path in data_table_config_folder_path.glob("*.json"):
        data_table_config = read_data_table_config(data_table_config_file_path)
        data_table_configs.append(data_table_config)
    return data_table_configs


def find_data_config_from_name(data_table_configs, data_table_name):
    for data_table_config in data_table_configs:
        if data_table_config["data_table_name"] == data_table_name:
            return data_table_config
    return None


def remove_one_and_rename_rest_bkup_files(
    data_folder, data_filename_main_part, bkup_data_files
):
    bkup_data_files = sorted(bkup_data_files)
    os.remove(os.path.join(data_folder, bkup_data_files[0]))
    bkup_data_files.remove(bkup_data_files[0])
    for idx, bkup_file in enumerate(bkup_data_files):
        bkup_rename_filename = data_filename_main_part + "_bkup" + str(idx) + ".json"
        shutil.move(
            os.path.join(data_folder, bkup_file),
            os.path.join(data_folder, bkup_rename_filename),
        )


def back_up_data_file(data_table_path, bkup_no=5):
    data_filename = data_table_path.name
    data_folder = data_table_path.parent
    back_up_folder = data_folder / "back_up"
    if not back_up_folder.exists():
        os.makedirs(back_up_folder)
    data_filename_main_part = data_table_path.stem
    bkup_data_files = [
        file
        for file in os.listdir(back_up_folder)
        if re.match(f"^{data_filename_main_part}.*_bkup.*", file)
        and not os.path.isdir(file)
    ]
    # if there are more than 5 back up files remove the oldest and rename others
    if len(bkup_data_files) >= bkup_no:
        remove_one_and_rename_rest_bkup_files(
            back_up_folder, data_filename_main_part, bkup_data_files
        )
    # backup the current password file
    bkup_filename = (
        data_filename_main_part + "_bkup" + str(len(bkup_data_files)) + ".json"
    )
    shutil.copy(
        os.path.join(data_folder, data_filename),
        os.path.join(back_up_folder, bkup_filename),
    )
    logging.info(f"backed up data file {data_folder/data_filename}")


def get_column_name_from_qtable_item(item, data_config_columns):
    item_column_idx = item.column()
    return data_config_columns[item_column_idx]


def get_key_column_value_from_qtable_item(item, table_widget):
    return table_widget.item(item.row(), 0).text()

def get_data_table_content_value_from_key(
    data_table_contents, key_column_name, key_column_val, column_name
):
    """Get the value of the specific column of data table content"""
    data_table_content_matches = [
        data_table_content
        for data_table_content in data_table_contents
        if data_table_content[key_column_name] == key_column_val
    ]
    if len(data_table_content_matches) > 0:
        data_table_content = data_table_content_matches[0]
        return data_table_content[column_name]
