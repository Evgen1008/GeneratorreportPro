import os
import sys
import shutil


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )


BASE_DIR = get_base_dir()


# Рабочая папка пользователя
DATA_DIR = os.path.join(
    os.environ["USERPROFILE"],
    "Documents",
    "GeneratorReportPro"
)


REPORTS_DIR = os.path.join(
    DATA_DIR,
    "reports"
)

TEMPLATES_DIR = os.path.join(
    DATA_DIR,
    "templates"
)

DATABASE_FILE = os.path.join(
    DATA_DIR,
    "generator_report.db"
)


def init_user_data():
    """
    Первое создание пользовательских данных
    """

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    os.makedirs(
        REPORTS_DIR,
        exist_ok=True
    )

    os.makedirs(
        TEMPLATES_DIR,
        exist_ok=True
    )


    # копируем базу только если её нет
    if not os.path.exists(DATABASE_FILE):

        source_db = os.path.join(
            BASE_DIR,
            "data",
            "generator_report.db"
        )

        if os.path.exists(source_db):
            shutil.copy2(
                source_db,
                DATABASE_FILE
            )


    # копируем шаблоны
    source_templates = os.path.join(
        BASE_DIR,
        "data",
        "templates"
    )

    if os.path.exists(source_templates):

        for file in os.listdir(source_templates):

            src = os.path.join(
                source_templates,
                file
            )

            dst = os.path.join(
                TEMPLATES_DIR,
                file
            )

            if not os.path.exists(dst):
                shutil.copy2(
                    src,
                    dst
                )


# запуск инициализации
init_user_data()