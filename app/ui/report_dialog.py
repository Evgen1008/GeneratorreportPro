# app/ui/report_dialog.py

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QComboBox,
    QRadioButton,
    QPushButton,
    QButtonGroup
)


class ReportDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(
            "Формирование отчёта"
        )

        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)


        # год

        year_layout = QHBoxLayout()

        year_layout.addWidget(
            QLabel("Год:")
        )

        self.year_box = QSpinBox()

        self.year_box.setRange(
            2020,
            2100
        )

        self.year_box.setValue(
            2026
        )

        year_layout.addWidget(
            self.year_box
        )

        layout.addLayout(
            year_layout
        )


        # месяц

        month_layout = QHBoxLayout()

        month_layout.addWidget(
            QLabel("Месяц:")
        )

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

        self.month_box.addItems(
            months
        )

        self.month_box.setCurrentIndex(
            6
        )

        month_layout.addWidget(
            self.month_box
        )

        layout.addLayout(
            month_layout
        )


        # декада

        layout.addWidget(
            QLabel("Декада:")
        )


        self.dec1 = QRadioButton(
            "01-10"
        )

        self.dec2 = QRadioButton(
            "11-20"
        )

        self.dec3 = QRadioButton(
            "21-31"
        )


        self.dec1.setChecked(
            True
        )


        self.group = QButtonGroup(
            self
        )

        self.group.addButton(
            self.dec1,
            1
        )

        self.group.addButton(
            self.dec2,
            2
        )

        self.group.addButton(
            self.dec3,
            3
        )


        layout.addWidget(
            self.dec1
        )

        layout.addWidget(
            self.dec2
        )

        layout.addWidget(
            self.dec3
        )


        # кнопки

        buttons = QHBoxLayout()


        self.ok_btn = QPushButton(
            "Создать"
        )

        self.cancel_btn = QPushButton(
            "Отмена"
        )


        self.ok_btn.clicked.connect(
            self.accept
        )

        self.cancel_btn.clicked.connect(
            self.reject
        )


        buttons.addWidget(
            self.ok_btn
        )

        buttons.addWidget(
            self.cancel_btn
        )


        layout.addLayout(
            buttons
        )


    def year(self):
        return self.year_box.value()


    def month(self):
        return self.month_box.currentIndex() + 1


    def decade(self):

        if self.dec1.isChecked():
            return 1

        if self.dec2.isChecked():
            return 2

        return 3