# Introduction

This is a GUI application to store various information as tables, called data tables in the context of this application.

- The application will allow to create data tables with columns defined by the user. All columns will store string values.
- The application will allow the user to add new data, edit data or remove data from data tables.
- It will allow to filter data tables among many data tables and navigate to the contents of that data table
- When viewing a certain data table contents, user can filter data by searching keywords for a specific column.

# Implementation

## Building environment

We will use FBS to build this application.
You can build a virtual environment with fbs. FBS only supports Python 3.6. So you will have to build
the virtual environment with Python 3.6. If you are using Windows, you can download an install Python 3.6 on your system
and then use it to create the virtual environment that will contain FBS libraries

```
python -m venv fbs-venv-py36
```

Then we install `fbs-tutorial` library into the virtual environment.

# Program walkthrough

## Main window

```MainWindow``` extends ```QMainWindow```. 
We pass application context to its constructor. We use ```ApplicationContext``` to access resources such as
- data table definitions (table name, column names)
- data table contents (table records)
- styles (to style various QtWidgets like QPushButton)

The attribute ```data_table_configs``` is a list of data table definitions. Each data table definition is
a json object with table name, full name and column names.

The attribute ```data_config_actions``` is a dictionary of ```QAction```s that will allow us to access each data table content.
We populate this dictionary by looping through data tables in ```data_table_configs```.
Each dictionary item is a key, value, with key being ```data_table_name``` and value being ```QAction```
We connect each ```QAction```'s ```triggered``` event to a function ```data_config_selected``` passing ```data_config``` as an argument.

If we coded it in the following way, it won't work. Because the argument of each function is resolved at the time of the execution. By the time each function is executed, the argument will always be the last item in data_configs.

```python
for data_config in data_configs:
    data_config_actions[data_config["data_table_name"]]=QAction(data_config["data_table_full_name"])
    data_config_actions[...].triggered.connect(self.data_config_action_selected,data_config)
```

Instead if we use ```partial``` we can prevent behavior mentioned above.

```python
from functools import partial

for data_config in data_configs:
    data_config_actions[data_config["data_table_name"]]=QAction(data_config["data_table_full_name"])
    data_config_actions[...].triggered.connect(partial(self.data_config_action_selected,data_config))
```

In its constructor ```MainWindow```
- reads data table definitions into ```data_table_configs```
- calls ```initializeUI``` function

```initializeUI``` function
- initializes ```menu_bar``` by calling ```self.menuBar()``` which is inherited from ```QMainWindow```

- initializes ```stacked_widget``` by instantiating ```QStackedWidget```. This widget will be set as a central widget and will contain all other widgets. Via ```QActions``` we navigate various widgets by calling ```setCurrentWidget``` method of the ```QStackedWidget```

- initializes ```new_data_table_widget``` by instantiating ```NewDataTableWidget```. We pass application context to ```NewDataTableWidget```. This class provides a form widget to create a new data table. We provide data table name and number of columns. Then we provide the names for each column.

- initializes data tables. Each data table is maintained in ```data_table_widgets``` dictionary, with key ```data_table_name``` and value ```DataTable```. ```DataTable``` provides ```data_table_window``` and ```new_data_table_content_window``` as member variables. When ```MainWindow``` tries to add a data table widget and its corresponding new data table widget into ```stacked_widget```, these member variables will be used.

- initializes data table actions list widget. This is done by instantiating ```DataTableActionsList```

- Create File menu and add data config actions list to File menu. This just adds a line to File menu to access the list of data table ```QAction```s

- Create data table actions menu. This will create a new menu and add data table ```QAction```s as individual lines. 
This function also takes care of creating a dictionary of data table actions, where for each item key is ```data_table_name``` and value is ```QAction```. Creation of this dictionary is accomplished by ```populate_data_config_actions``` function.