from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QDateEdit, QLabel
)
from PySide6.QtCore import QDate, Qt


class WorkCalendarWindow(QDialog):

    def __init__(self, db, parent=None):
        super().__init__(parent)

        self.db = db
        self.setWindowTitle("Календарь работы генераторов")
        self.resize(900, 500)

        self.layout = QVBoxLayout(self)

        top = QHBoxLayout()

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)

        # восстанавливаем последний сохранённый период
        last_period = self.db.get_last_calendar_period()

        if last_period:
            y, m, d = map(int, last_period.split("-"))
            self.start_date.setDate(QDate(y, m, d))
        else:
            self.start_date.setDate(QDate.currentDate())

        top.addWidget(QLabel("Начало декады:"))
        top.addWidget(self.start_date)

        self.layout.addLayout(top)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        buttons = QHBoxLayout()

        self.save_btn = QPushButton("Сохранить")
        self.all_btn = QPushButton("Выбрать все")
        self.clear_btn = QPushButton("Снять все")

        buttons.addWidget(self.all_btn)
        buttons.addWidget(self.clear_btn)
        buttons.addWidget(self.save_btn)

        self.layout.addLayout(buttons)

        self.generators = [
            g for g in self.db.get_generators()
            if str(g.get("status", "Рабочий")).strip() == "Рабочий"
        ]

        self.start_date.dateChanged.connect(self.refresh_calendar)

        self.build_table()
        self.load_calendar()

        self.save_btn.clicked.connect(self.save)
        self.all_btn.clicked.connect(self.select_all)
        self.clear_btn.clicked.connect(self.clear_all)


    def build_table(self):

        days = 10

        self.table.setRowCount(len(self.generators))
        self.table.setColumnCount(days + 1)

        headers = ["Генератор"]

        for i in range(days):
            headers.append(
                self.start_date.date()
                .addDays(i)
                .toString("dd.MM")
            )

        self.table.setHorizontalHeaderLabels(headers)

        for row, gen in enumerate(self.generators):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(gen["inventory"])
            )

            for col in range(1, days + 1):

                item = QTableWidgetItem()
                item.setText("✓")
                item.setCheckState(Qt.Checked)

                self.table.setItem(row, col, item)


    def load_calendar(self):

        start = self.start_date.date()
        end = start.addDays(9)

        records = self.db.get_work_calendar(
            start.toString("yyyy-MM-dd"),
            end.toString("yyyy-MM-dd")
        )

        saved = {}

        for row in records:
            saved[(row["inventory"], row["date"])] = row["worked"]

        for r, gen in enumerate(self.generators):

            for c in range(1, self.table.columnCount()):

                date = start.addDays(c - 1).toString("yyyy-MM-dd")

                if (gen["inventory"], date) in saved:
                    state = saved[(gen["inventory"], date)]
                    self.table.item(r, c).setCheckState(
                        Qt.Checked if state else Qt.Unchecked
                    )


    def select_all(self):

        for row in range(self.table.rowCount()):
            for col in range(1, self.table.columnCount()):
                self.table.item(row, col).setCheckState(Qt.Checked)


    def clear_all(self):

        for row in range(self.table.rowCount()):
            for col in range(1, self.table.columnCount()):
                self.table.item(row, col).setCheckState(Qt.Unchecked)


    def save(self):

        start = self.start_date.date()

        self.db.save_calendar_period(
            start.toString("yyyy-MM-dd")
        )

        for row, gen in enumerate(self.generators):

            inventory = gen["inventory"]

            for col in range(1, self.table.columnCount()):

                date = start.addDays(col - 1).toString("yyyy-MM-dd")

                worked = 1 if self.table.item(row, col).checkState() == Qt.Checked else 0

                self.db.save_work_day(
                    inventory,
                    date,
                    worked
                )

        self.accept()


    def refresh_calendar(self):
        self.build_table()
        self.load_calendar()
