# ДОБАВЛЕНИЕ ДЛЯ database.py
# Вставить в Database.__init__ после create_fuel_tables():
#
# self.create_fuel_distribution_table()
#
# И добавить следующие методы в класс Database:

def create_fuel_distribution_table(self):

    cursor = self.conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fuel_distribution (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        inventory TEXT,
        liters REAL DEFAULT 0
    )
    """)

    self.conn.commit()


def clear_fuel_distribution(self):

    cursor = self.conn.cursor()

    cursor.execute("""
    DELETE FROM fuel_distribution
    """)

    self.conn.commit()


def add_fuel_distribution(
        self,
        date,
        inventory,
        liters
    ):

    cursor = self.conn.cursor()

    cursor.execute("""
    INSERT INTO fuel_distribution
    (
        date,
        inventory,
        liters
    )
    VALUES (?,?,?)
    """,
    (
        date,
        inventory,
        liters
    ))

    self.conn.commit()


def get_fuel_distribution(self):

    cursor = self.conn.cursor()

    cursor.execute("""
    SELECT *
    FROM fuel_distribution
    ORDER BY date, inventory
    """)

    return self._rows_to_dicts(cursor.fetchall())
