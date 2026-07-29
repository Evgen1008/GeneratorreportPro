from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDateEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QHBoxLayout,
    QInputDialog
)

from PySide6.QtCore import QDate

from app.ui.fuel_distribution_window import FuelDistributionWindow


class FuelWindow(QWidget):

    def __init__(self, database):
        super().__init__()

        self.db = database

        self.setWindowTitle("Получение топлива")
        self.resize(700, 600)

        self.selected_id = None
        self.current_generator = None

        self.create_ui()
        self.load_table()
        self.update_report()


    def create_ui(self):

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel("Дата получения топлива:")
        )

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)

        layout.addWidget(self.date_edit)


        layout.addWidget(
            QLabel("Количество литров:")
        )

        self.liters_edit = QLineEdit()
        self.liters_edit.setPlaceholderText("Например: 1000")

        layout.addWidget(self.liters_edit)


        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton("Сохранить")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")
        self.distribution_btn = QPushButton("Распределение топлива")

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.distribution_btn)

        self.save_btn.clicked.connect(
            self.save_fuel
        )

        layout.addLayout(btn_layout)

        self.edit_btn.clicked.connect(self.edit_fuel)
        self.delete_btn.clicked.connect(self.delete_fuel)
        self.distribution_btn.clicked.connect(self.open_distribution)


        layout.addWidget(
            QLabel("Журнал получения топлива:")
        )


        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(
            [
                "Дата",
                "Получено, л"
            ]
        )

        layout.addWidget(self.table)


        period_layout = QHBoxLayout()


        self.month_box = QComboBox()

        months = [
            "Январь",
            "Февраль",
            "Март",
            "Апрель",
            "Май",
            "Июнь",
            "Июль",
            "Август",
            "Сентябрь",
            "Октябрь",
            "Ноябрь",
            "Декабрь"
        ]

        self.month_box.addItems(months)

        self.month_box.setCurrentIndex(
            QDate.currentDate().month() - 1
        )


        self.year_box = QComboBox()

        for year in range(2024, 2035):
            self.year_box.addItem(str(year))

        self.year_box.setCurrentText(
            str(QDate.currentDate().year())
        )


        self.decade_box = QComboBox()

        self.decade_box.addItems(
            [
                "Весь месяц",
                "1 декада (01-10)",
                "2 декада (11-20)",
                "3 декада (21-конец)"
            ]
        )


        period_layout.addWidget(self.month_box)
        period_layout.addWidget(self.year_box)
        period_layout.addWidget(self.decade_box)


        layout.addLayout(period_layout)


        self.report_label = QLabel()

        layout.addWidget(
            self.report_label
        )


        self.month_box.currentIndexChanged.connect(self.load_table)
        self.year_box.currentIndexChanged.connect(self.load_table)
        self.decade_box.currentIndexChanged.connect(self.load_table)

        self.month_box.currentIndexChanged.connect(self.update_report)
        self.year_box.currentIndexChanged.connect(self.update_report)
        self.decade_box.currentIndexChanged.connect(self.update_report)


    def save_fuel(self):

        try:

            liters = float(
                self.liters_edit.text()
            )

        except:

            QMessageBox.warning(
                self,
                "Ошибка",
                "Введите количество литров"
            )

            return


        date = self.date_edit.date().toString(
            "dd.MM.yyyy"
        )


        # Приход топлива общий.
        # Распределение между генераторами выполняет расчётный модуль.
        self.db.add_fuel_income(
            "",
            date,
            liters,
            ""
        )


        self.liters_edit.clear()

        self.load_table()
        self.update_report()


        QMessageBox.information(
            self,
            "Готово",
            "Топливо добавлено"
        )


    def load_generators(self):

        self.generator_box.clear()

        for g in self.db.get_generators():
            self.generator_box.addItem(g["inventory"])


    def load_table(self):

        rows = self.db.get_fuel_income()

        month = self.month_box.currentIndex() + 1
        year = int(self.year_box.currentText())
        decade = self.decade_box.currentIndex()

        filtered = []

        for row in rows:
            date = row["date"]
            try:
                day, m, y = map(int, date.split("."))
            except:
                continue

            if m == month and y == year:
                if decade == 0:
                    filtered.append(row)
                elif decade == 1 and day <= 10:
                    filtered.append(row)
                elif decade == 2 and 11 <= day <= 20:
                    filtered.append(row)
                elif decade == 3 and day >= 21:
                    filtered.append(row)

        self.table.setRowCount(len(filtered))

        for i, row in enumerate(filtered):
            item_date = QTableWidgetItem(str(row["date"]))
            item_date.setData(256, row["id"])

            self.table.setItem(i, 0, item_date)
            self.table.setItem(i, 1, QTableWidgetItem(str(row["liters"])))


    def update_report(self):

        rows = self.db.get_fuel_income()

        month = self.month_box.currentIndex() + 1
        year = int(self.year_box.currentText())

        decade = self.decade_box.currentIndex()


        total_month = 0
        total_decade = 0


        for row in rows:

            date = row["date"]
            liters = float(row["liters"] or 0)


            try:
                day, m, y = map(
                    int,
                    date.split(".")
                )

            except:
                continue


            if m == month and y == year:

                total_month += liters


                if decade == 0:
                    total_decade = total_month

                elif decade == 1 and day <= 10:
                    total_decade += liters

                elif decade == 2 and 11 <= day <= 20:
                    total_decade += liters

                elif decade == 3 and day >= 21:
                    total_decade += liters


        total_all = self.db.get_total_fuel_income()


        self.report_label.setText(
            f"Получено за период: {total_decade} л\n"
            f"Получено за месяц: {total_month} л\n"
            f"Всего получено: {total_all} л"
        )
   

    def edit_fuel(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return

        fuel_id = self.table.item(row, 0).data(256)
        old_date = self.table.item(row, 0).text()
        old_liters = float(self.table.item(row, 1).text() or 0)

        date, ok = QInputDialog.getText(
            self,
            "Редактирование даты",
            "Дата (дд.мм.гггг):",
            text=old_date
        )

        if not ok:
            return

        liters, ok = QInputDialog.getDouble(
            self,
            "Редактирование количества",
            "Литры:",
            old_liters
        )

        if ok:
            self.db.update_fuel_income(
                fuel_id,
                "",
                date,
                liters,
                ""
            )
            self.load_table()
            self.update_report()


    def open_distribution(self):

        year = int(
            self.year_box.currentText()
        )

        month = (
            self.month_box.currentIndex()
            + 1
        )

        decade_index = (
            self.decade_box.currentIndex()
        )

        # Если выбран весь месяц -
        # открываем текущую декаду
        if decade_index == 0:

            from datetime import datetime

            day = datetime.now().day

            if day <= 10:
                decade = 1
            elif day <= 20:
                decade = 2
            else:
                decade = 3

        else:
            decade = decade_index


        self.distribution_window = FuelDistributionWindow(
            self.db,
            year,
            month,
            decade,
            self
        )

        self.distribution_window.show()


    def delete_fuel(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return

        fuel_id = self.table.item(row, 0).data(256)
        date = self.table.item(row, 0).text()
        liters = self.table.item(row, 1).text()

        answer = QMessageBox.question(
            self,
            "Удаление",
            f"Удалить запись?\\n{date} - {liters} л"
        )

        if answer == QMessageBox.Yes:
            self.db.delete_fuel_income(fuel_id)
            self.load_table()
            self.update_report()
