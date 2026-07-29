from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QDoubleSpinBox,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QComboBox,
)


class GeneratorDialog(QDialog):

    def __init__(self, parent=None, generator=None):
        super().__init__(parent)

        self.generator = generator
        self.db = getattr(parent, 'db', None)

        self.setWindowTitle(
            "Генератор"
        )

        self.resize(750, 650)

        layout = QVBoxLayout(self)

        form = QFormLayout()


        self.ed_inventory = QLineEdit()
        self.cb_status = QComboBox()
        self.cb_status.addItems(['Рабочий', 'Нерабочий'])
        self.ed_name = QTextEdit()
        self.ed_name.setFixedHeight(60)
        self.ed_department = QTextEdit()
        self.ed_department.setFixedHeight(60)
        self.ed_type = QLineEdit()
        self.ed_model = QLineEdit()
        self.ed_serial = QLineEdit()
        self.ed_object = QTextEdit()
        self.ed_object.setFixedHeight(60)

        self.ed_consumption = QDoubleSpinBox()
        self.ed_consumption.setDecimals(2)
        self.ed_consumption.setMaximum(999)

        self.ed_initial_balance = QDoubleSpinBox()
        self.ed_initial_balance.setDecimals(2)
        self.ed_initial_balance.setMaximum(999999)

        self.ed_template = QLineEdit()
        self.ed_template.setReadOnly(True)

        self.ed_note = QTextEdit()
        self.ed_note.setFixedHeight(80)


        form.addRow(
            "Инвентарный номер *",
            self.ed_inventory
        )

        form.addRow(
            "Статус",
            self.cb_status
        )

        form.addRow(
            "Наименование",
            self.ed_name
        )

        form.addRow(
            "Наименование подразделения",
            self.ed_department
        )

        form.addRow(
            "Тип генератора",
            self.ed_type
        )

        form.addRow(
            "Модель",
            self.ed_model
        )

        form.addRow(
            "Серийный номер",
            self.ed_serial
        )

        form.addRow(
            "Объект",
            self.ed_object
        )

        form.addRow(
            "Расход топлива (л/ч)",
            self.ed_consumption
        )

        form.addRow(
            "Остаток топлива на начало (л)",
            self.ed_initial_balance
        )


        btn_template = QPushButton(
            "Выбрать Excel..."
        )

        btn_template.clicked.connect(
            self.select_template
        )


        form.addRow(
            "Шаблон Excel",
            self.ed_template
        )

        form.addRow(
            "",
            btn_template
        )


        form.addRow(
            "Примечание",
            self.ed_note
        )


        layout.addLayout(form)


        buttons = QHBoxLayout()

        self.btn_save = QPushButton(
            "Сохранить"
        )

        self.btn_cancel = QPushButton(
            "Отмена"
        )


        self.btn_save.clicked.connect(
            self.accept
        )

        self.btn_cancel.clicked.connect(
            self.reject
        )


        buttons.addStretch()

        buttons.addWidget(
            self.btn_save
        )

        buttons.addWidget(
            self.btn_cancel
        )


        layout.addLayout(buttons)


        if generator:
            self.load_generator(generator)



    # -------------------------------------------------

    def select_template(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите шаблон Excel",
            "",
            "Excel (*.xlsx)"
        )

        if filename:
            self.ed_template.setText(
                filename
            )


    # -------------------------------------------------

    def load_generator(self, generator):

        self.ed_inventory.setText(
            generator["inventory"]
        )

        self.cb_status.setCurrentText(
            generator.get('status', 'Рабочий') or 'Рабочий'
        )

        self.ed_name.setPlainText(
            generator["name"] or ""
        )

        self.ed_department.setPlainText(
            generator["department"] or ""
        )

        self.ed_type.setText(
            generator["generator_type"] or ""
        )

        self.ed_model.setText(
            generator["model"] or ""
        )

        self.ed_serial.setText(
            generator["serial"] or ""
        )

        self.ed_object.setPlainText(
            generator["location"] or ""
        )

        self.ed_consumption.setValue(
            generator["consumption"] or 0
        )

        self.ed_template.setText(
            generator["template"] or ""
        )

        balance = generator.get("initial_balance", 0) or 0

        try:
            if self.db:
                period = self.db.get_last_calendar_period()

                if period:
                    from datetime import datetime

                    first_date = datetime.strptime(
                        period,
                        "%Y-%m-%d"
                    ).date()

                    if first_date.day <= 10:
                        decade = 1
                    elif first_date.day <= 20:
                        decade = 2
                    else:
                        decade = 3

                    balance = self.db.get_start_balance(
                        generator["inventory"],
                        first_date.year,
                        first_date.month,
                        decade,
                        first_date
                    ) or balance

        except Exception:
            pass

        self.ed_initial_balance.setValue(balance)

        self.ed_note.setPlainText(
            generator["note"] or ""
        )



    # -------------------------------------------------

    def get_data(self):

        return {

            "inventory":
                self.ed_inventory.text(),

            "status":
                self.cb_status.currentText(),

            "name":
                self.ed_name.toPlainText(),

            "department":
                self.ed_department.toPlainText(),

            "generator_type":
                self.ed_type.text(),

            "model":
                self.ed_model.text(),

            "serial":
                self.ed_serial.text(),

            "location":
                self.ed_object.toPlainText(),

            "consumption":
                self.ed_consumption.value(),

            "initial_balance":
                self.ed_initial_balance.value(),

            "template":
                self.ed_template.text(),

            "note":
                self.ed_note.toPlainText(),
        }