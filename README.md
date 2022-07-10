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
