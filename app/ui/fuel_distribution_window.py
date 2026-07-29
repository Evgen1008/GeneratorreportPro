from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QSpinBox,
    QMessageBox
)

from PySide6.QtGui import QFont

from app.services.fuel_calculator import FuelCalculator


class FuelDistributionWindow(QDialog):

    def __init__(self, database, year, month, decade, parent=None):
        super().__init__(parent)

        self.db = database
        self.year = year
        self.month = month
        self.decade = decade
        self.calculator = FuelCalculator(self.db)
        self.manual_changes = set()

        self.setWindowTitle("Распределение топлива")
        self.resize(1000, 600)

        self.create_ui()
        self.load_table()


    def normalize_date(self, value):
        text = str(value)

        if "." in text:
            try:
                d, m, y = text.split(".")
                return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
            except:
                pass

        return text[:10]


    def create_ui(self):

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel(
                f"Распределение топлива {self.month:02d}.{self.year}, декада {self.decade}"
            )
        )

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.auto_button = QPushButton("Вернуть авторасчёт")
        layout.addWidget(self.auto_button)
        self.auto_button.clicked.connect(self.restore_auto)

        self.save_button = QPushButton("Сохранить")
        layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save)


    def load_table(self):

        all_generators = self.db.get_generators()

        rows = {}

        for fuel in self.db.get_fuel_income():

            day = self.normalize_date(fuel["date"])

            try:
                y, m, d = map(int, day.split("-"))
            except:
                continue

            if y != self.year or m != self.month:
                continue

            if self.decade == 1 and d > 10:
                continue

            if self.decade == 2 and (d < 11 or d > 20):
                continue

            if self.decade == 3 and d < 21:
                continue

            rows[day] = rows.get(day, 0) + float(fuel["liters"] or 0)


        # Заголовки создаём после определения работающих генераторов
        # чтобы не показывать неработающие

        self.table.setRowCount(len(rows))

        self.current_display_inventory = []


        # Определяем генераторы для отображения
        # по календарю работы

        display_generators = []

        for day in rows:

            working_inventory = self.db.get_working_generators(day)

            for g in all_generators:
                if g["inventory"] in working_inventory:
                    if g not in display_generators:
                        display_generators.append(g)


        headers = ["Дата", "Получено"]

        for g in display_generators:
            headers.append(g["inventory"])
            self.current_display_inventory.append(g["inventory"])

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)


        for row, day in enumerate(rows):

            working_inventory = self.db.get_working_generators(day)

            generators = [
                g for g in display_generators
                if g["inventory"] in working_inventory
            ]


            self.table.setItem(
                row,
                0,
                QTableWidgetItem(day)
            )

            received = rows[day]

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(str(received))
            )


            # Сначала пробуем загрузить сохранённое ручное распределение
            saved_distribution = self.db.get_fuel_distribution(
                day,
                day
            )

            saved = {}
            saved_manual = {}

            for item in saved_distribution:
                saved[item["generator"]] = item["liters"]
                saved_manual[item["generator"]] = item.get("manual", 0)


            if saved:

                distribution = saved

            else:

                distribution = self.calculator.distribute_fuel(
                    received,
                    generators,
                    {}
                )


            for col, gen in enumerate(display_generators, start=2):

                spin = QSpinBox()
                spin.setMaximum(9999)
                spin.setSingleStep(5)

                value = int(
                    distribution.get(
                        gen["inventory"],
                        0
                    )
                )

                spin.setValue(value)

                if saved_manual.get(gen["inventory"], 0):
                    font = spin.font()
                    font.setBold(True)
                    spin.setFont(font)


                spin.valueChanged.connect(
                    lambda value, r=row, c=col, s=spin:
                    self.mark_manual_change(r, c, s)
                )

                self.table.setCellWidget(
                    row,
                    col,
                    spin
                )


    def mark_manual_change(self, row, col, spin):

        self.manual_changes.add((row, col))

        font = spin.font()
        font.setBold(True)
        spin.setFont(font)



    def restore_auto(self):

        result = QMessageBox.question(
            self,
            "Автораспределение",
            "Вернуть автоматическое распределение?\n\n"
            "Все ручные изменения будут отменены.",
            QMessageBox.Yes | QMessageBox.No
        )

        if result != QMessageBox.Yes:
            return


        for row in range(self.table.rowCount()):

            received = float(
                self.table.item(row, 1).text()
            )

            generators = []

            for col in range(2, self.table.columnCount()):

                header = self.table.horizontalHeaderItem(col)

                if header:

                    for g in self.db.get_generators():

                        if g["inventory"] == header.text():

                            generators.append(g)
                            break


            distribution = self.calculator.distribute_fuel(
                received,
                generators,
                {}
            )


            for col in range(2, self.table.columnCount()):

                header = self.table.horizontalHeaderItem(col)

                if not header:
                    continue


                spin = self.table.cellWidget(row, col)

                if spin:

                    spin.blockSignals(True)

                    spin.setValue(
                        int(
                            distribution.get(
                                header.text(),
                                0
                            )
                        )
                    )

                    spin.blockSignals(False)

                    font = spin.font()
                    font.setBold(False)
                    spin.setFont(font)


        self.manual_changes.clear()



    def validate_distribution(self, row):

        received = float(
            self.table.item(row, 1).text()
        )

        total = 0

        for col in range(2, self.table.columnCount()):

            spin = self.table.cellWidget(row, col)

            if spin:
                total += spin.value()


        if total != received:

            QMessageBox.warning(
                self,
                "Ошибка распределения",
                f"Дата: {self.table.item(row,0).text()}\n\n"
                f"Получено: {received} л\n"
                f"Распределено: {total} л\n\n"
                f"Количество должно быть равно полученному."
            )

            return False

        return True


    def save(self):

        generators = self.db.get_generators()

        # сохраняем только реально отображаемые колонки
        generators = [
            g for g in generators
            if g["inventory"] in self.current_display_inventory
        ]

        for row in range(self.table.rowCount()):

            if not self.validate_distribution(row):
                return

            day = self.table.item(row, 0).text()

            self.db.clear_fuel_distribution(day)

            for col, gen in enumerate(generators, start=2):

                spin = self.table.cellWidget(row, col)

                if spin:

                    manual = 1 if (row, col) in self.manual_changes else 0

                    self.db.add_fuel_distribution(
                        gen["inventory"],
                        day,
                        spin.value(),
                        manual
                    )

        self.accept()
