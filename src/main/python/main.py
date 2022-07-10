from fbs_runtime.application_context.PyQt5 import ApplicationContext
from data_table.main_window import MainWindow
import pathlib
import sys

if __name__ == "__main__":
    appctxt = ApplicationContext()  # 1. Instantiate ApplicationContext
    style_sheet = pathlib.Path(appctxt.get_resource("styles/mystyles.qss")).read_text()
    appctxt.app.setStyleSheet(style_sheet)
    main_window = MainWindow(appctxt)
    exit_code = appctxt.app.exec_()  # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
