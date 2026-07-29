# database.py
# Исправленная версия для GeneratorreportPro

import sqlite3
import os


class Database:

    def _row_to_dict(self, row):
        if row is None:
            return None
        return dict(row)

    def _rows_to_dicts(self, rows):
        return [dict(r) for r in rows]

    def __init__(self, db_name="data/generator_report.db"):

        os.makedirs(
            os.path.dirname(db_name),
            exist_ok=True
        )

        self.conn = sqlite3.connect(db_name)

        self.conn.row_factory = sqlite3.Row

        self.create_tables()
        self.create_fuel_tables()
        self.create_report_tables()
        self.create_work_calendar_table()
        self.create_work_calendar_settings_table()



    # ==========================
    # Генераторы
    # ==========================

    def create_tables(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS generators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory TEXT UNIQUE,
            name TEXT,
            department TEXT,
            generator_type TEXT,
            model TEXT,
            serial TEXT,
            location TEXT,
            consumption REAL,
            template TEXT,
            note TEXT,
            active INTEGER DEFAULT 1
        )
        """)

        self.conn.commit()



    def add_generator(self, data):

        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO generators
        (
            inventory,
            name,
            department,
            generator_type,
            model,
            serial,
            location,
            consumption,
            template,
            note
        )
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
        (
            data["inventory"],
            data["name"],
            data["department"],
            data["generator_type"],
            data["model"],
            data["serial"],
            data["location"],
            data["consumption"],
            data["template"],
            data["note"]
        ))

        self.conn.commit()



    def get_generators(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM generators
        WHERE active=1
        ORDER BY inventory
        """)

        return self._rows_to_dicts(cursor.fetchall())



    def get_generator(self, inventory):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM generators
        WHERE inventory=?
        """,
        (inventory,))

        return self._row_to_dict(cursor.fetchone())



    def update_generator(
            self,
            inventory,
            data
        ):

        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE generators
        SET
            name=?,
            department=?,
            generator_type=?,
            model=?,
            serial=?,
            location=?,
            consumption=?,
            template=?,
            note=?
        WHERE inventory=?
        """,
        (
            data["name"],
            data["department"],
            data["generator_type"],
            data["model"],
            data["serial"],
            data["location"],
            data["consumption"],
            data["template"],
            data["note"],
            inventory
        ))

        self.conn.commit()



    def update_generator_full(
            self,
            old_inventory,
            data
        ):

        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE generators
        SET
            inventory=?,
            name=?,
            department=?,
            generator_type=?,
            model=?,
            serial=?,
            location=?,
            consumption=?,
            template=?,
            note=?
        WHERE inventory=?
        """,
        (
            data["inventory"],
            data["name"],
            data["department"],
            data["generator_type"],
            data["model"],
            data["serial"],
            data["location"],
            data["consumption"],
            data["template"],
            data["note"],
            old_inventory
        ))

        self.conn.commit()



    def archive_generator(self, inventory):

        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE generators
        SET active=0
        WHERE inventory=?
        """,
        (inventory,))

        self.conn.commit()
        # ==========================
    # Топливо
    # ==========================

    def create_fuel_tables(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fuel_income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory TEXT,
            date TEXT,
            liters REAL,
            comment TEXT
        )
        """)

        self.conn.commit()



    def add_fuel_income(
            self,
            inventory,
            date,
            liters,
            comment=""
        ):

        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO fuel_income
        (
            inventory,
            date,
            liters,
            comment
        )
        VALUES (?,?,?,?)
        """,
        (
            inventory,
            date,
            liters,
            comment
        ))

        self.conn.commit()



    def update_fuel_income(
            self,
            fuel_id,
            inventory,
            date,
            liters,
            comment=""
        ):

        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE fuel_income
        SET
            inventory=?,
            date=?,
            liters=?,
            comment=?
        WHERE id=?
        """,
        (
            inventory,
            date,
            liters,
            comment,
            fuel_id
        ))

        self.conn.commit()



    def delete_fuel_income(
            self,
            fuel_id
        ):

        cursor = self.conn.cursor()

        cursor.execute("""
        DELETE FROM fuel_income
        WHERE id=?
        """,
        (fuel_id,))

        self.conn.commit()



    def get_fuel_income(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM fuel_income
        ORDER BY date
        """)

        return self._rows_to_dicts(cursor.fetchall())



    def get_total_fuel_income(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT SUM(liters)
        FROM fuel_income
        """)

        result = cursor.fetchone()[0]

        return result or 0



    # ==========================
    # Ежедневные отчёты
    # ==========================

    def create_report_tables(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS generator_daily_report (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory TEXT,
            date TEXT,
            received REAL DEFAULT 0,
            hours INTEGER DEFAULT 0,
            consumption REAL DEFAULT 0,
            fuel_used REAL DEFAULT 0,
            balance REAL DEFAULT 0
        )
        """)

        self.conn.commit()



    def get_last_balance(
            self,
            inventory,
            date
        ):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT balance
        FROM generator_daily_report
        WHERE inventory=?
        AND date<?
        ORDER BY date DESC
        LIMIT 1
        """,
        (
            inventory,
            date
        ))

        row = cursor.fetchone()

        if row:
            return row["balance"]

        return 0



    def get_daily_report(
            self,
            inventory,
            start_date,
            end_date
        ):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM generator_daily_report
        WHERE inventory=?
        AND date BETWEEN ? AND ?
        ORDER BY date
        """,
        (
            inventory,
            start_date,
            end_date
        ))

        return self._rows_to_dicts(cursor.fetchall())



    def save_daily_report(
            self,
            inventory,
            date,
            received,
            hours,
            consumption,
            fuel_used,
            balance
        ):

        cursor = self.conn.cursor()


        cursor.execute("""
        SELECT id
        FROM generator_daily_report
        WHERE inventory=?
        AND date=?
        """,
        (
            inventory,
            date
        ))


        row = cursor.fetchone()



        if row:

            cursor.execute("""
            UPDATE generator_daily_report
            SET
                received=?,
                hours=?,
                consumption=?,
                fuel_used=?,
                balance=?
            WHERE id=?
            """,
            (
                received,
                hours,
                consumption,
                fuel_used,
                balance,
                row["id"]
            ))


        else:

            cursor.execute("""
            INSERT INTO generator_daily_report
            (
                inventory,
                date,
                received,
                hours,
                consumption,
                fuel_used,
                balance
            )
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                inventory,
                date,
                received,
                hours,
                consumption,
                fuel_used,
                balance
            ))


        self.conn.commit()





    # ==========================
    # Календарь работы генераторов
    # ==========================

    def create_work_calendar_table(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS generator_work_calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory TEXT,
            date TEXT,
            worked INTEGER DEFAULT 1,
            UNIQUE(inventory, date)
        )
        """)

        self.conn.commit()


    def save_work_day(
            self,
            inventory,
            date,
            worked
        ):

        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO generator_work_calendar
        (
            inventory,
            date,
            worked
        )
        VALUES (?,?,?)
        ON CONFLICT(inventory,date)
        DO UPDATE SET worked=excluded.worked
        """,
        (
            inventory,
            date,
            worked
        ))

        self.conn.commit()


    def get_working_generators(
            self,
            date
        ):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT inventory
        FROM generator_work_calendar
        WHERE date=?
        AND worked=1
        """,
        (date,))

        return [
            row["inventory"]
            for row in cursor.fetchall()
        ]


    def get_work_calendar(
            self,
            start_date,
            end_date
        ):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM generator_work_calendar
        WHERE date BETWEEN ? AND ?
        ORDER BY date, inventory
        """,
        (
            start_date,
            end_date
        ))

        return self._rows_to_dicts(cursor.fetchall())


    # ==========================
    # Настройки периода календаря
    # ==========================

    def create_work_calendar_settings_table(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_calendar_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT
        )
        """)

        self.conn.commit()


    def save_calendar_period(self, start_date):

        cursor = self.conn.cursor()

        cursor.execute("""
        DELETE FROM work_calendar_settings
        """)

        cursor.execute("""
        INSERT INTO work_calendar_settings
        (start_date)
        VALUES (?)
        """,
        (start_date,))

        self.conn.commit()


    def get_last_calendar_period(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT start_date
        FROM work_calendar_settings
        ORDER BY id DESC
        LIMIT 1
        """)

        row = cursor.fetchone()

        if row:
            return row["start_date"]

        return None



    def close(self):

        self.conn.close()