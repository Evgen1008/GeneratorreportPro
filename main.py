import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.utils.paths import (
    DATA_DIR,
    REPORTS_DIR,
    TEMPLATES_DIR,
    init_user_data
)


def create_folders():
    """
    Создание пользовательских папок
    """

    Path(DATA_DIR).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(REPORTS_DIR).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(TEMPLATES_DIR).mkdir(
        parents=True,
        exist_ok=True
    )


def main():

    create_folders()

    init_user_data()

    app = QApplication(sys.argv)

    from app.database.database import Database

    database = Database()

    window = MainWindow(database)
    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()