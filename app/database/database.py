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

    def __init__(self, db_name=None):

        if db_name is None:
            try:
                from app.utils.paths import DATABASE_FILE
                db_name = DATABASE_FILE
            except Exception:
                project_root = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "..")
                )
                db_name = os.path.join(
                    project_root,
                    "data",
                    "generator_report.db"
                )

        os.makedirs(os.path.dirname(db_name), exist_ok=True)

        self.conn = sqlite3.connect(db_name)
        print("DATABASE USED:", db_name)
        self.conn.row_factory = sqlite3.Row

        self.create_tables()
        self.create_fuel_tables()
        self.create_report_tables()
        self.create_fuel_distribution_table()
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
            initial_balance REAL DEFAULT 0,
            previous_balance REAL DEFAULT 0,
            active INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Рабочий',
            sort_order INTEGER DEFAULT 0
        )
        """)

        self.conn.commit()

        try:
            cursor.execute(
                "ALTER TABLE generators ADD COLUMN status TEXT DEFAULT 'Рабочий'"
            )
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

        # добавляем поле остатка прошлого отчёта
        try:
            cursor.execute(
                "ALTER TABLE generators ADD COLUMN previous_balance REAL DEFAULT 0"
            )
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

        # добавляем поле порядка отображения
        try:
            cursor.execute(
                "ALTER TABLE generators ADD COLUMN sort_order INTEGER DEFAULT 0"
            )
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

        # добавляем поле начального остатка для старых баз
        try:
            cursor.execute(
                "ALTER TABLE generators ADD COLUMN initial_balance REAL DEFAULT 0"
            )
            self.conn.commit()
        except sqlite3.OperationalError:
            pass



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
            note,
            initial_balance,
            status,
            sort_order
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
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
            data.get("initial_balance", 0),
            data.get("status", "Рабочий"),
            data.get("sort_order", 0)
        ))

        self.conn.commit()



    def get_generators(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM generators
        WHERE active=1
        ORDER BY
            CASE WHEN status='Нерабочий' THEN 1 ELSE 0 END,
            sort_order,
            inventory
        """)

        return self._rows_to_dicts(cursor.fetchall())

    def debug_calendar(self):

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT *
            FROM generator_work_calendar
            WHERE date LIKE '2026-07%'
        """)

        rows = cursor.fetchall()

        for r in rows:
            print(r)
    def get_working_generators(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM generators
        WHERE active=1
        AND status='Рабочий'
        ORDER BY
        sort_order,
        inventory
        """)

        return self._rows_to_dicts(
        cursor.fetchall()
        )


    def get_generator(self, inventory):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM generators
        WHERE inventory=?
        """,
        (inventory,))

        row = cursor.fetchone()

        print("LOAD:", row["inventory"], row["initial_balance"])

        return self._row_to_dict(row)



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
            note=?,
            initial_balance=?,
            status=?,
            sort_order=?
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
            data.get("initial_balance", 0),
            data.get("status", "Рабочий"),
            data.get("sort_order", 0),
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
            note=?,
            initial_balance=?,
            status=?,
            sort_order=?
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
            data.get("initial_balance", 0),
            data.get("status", "Рабочий"),
            data.get("sort_order", 0),
            old_inventory
        ))

        self.conn.commit()
        print("SAVE:", data.get("inventory"), data.get("initial_balance"))


    def update_generator_order(self, inventories):

        cursor = self.conn.cursor()

        for index, inventory in enumerate(inventories):
            cursor.execute("""
            UPDATE generators
            SET sort_order=?
            WHERE inventory=?
            """, (index, inventory))

        self.conn.commit()


    def move_generator(self, inventory, direction):

        generators = self.get_generators()
        names = [g["inventory"] for g in generators]

        if inventory not in names:
            return

        index = names.index(inventory)
        new_index = index + direction

        if new_index < 0 or new_index >= len(names):
            return

        names[index], names[new_index] = names[new_index], names[index]
        self.update_generator_order(names)


    def archive_generator(self, inventory):

        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE generators
        SET active=0
        WHERE inventory=?
        """,
        (inventory,))

        self.conn.commit()

    def get_archived_generators(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM generators
        WHERE active=0
         ORDER BY inventory
        """)

        return self._rows_to_dicts(
            cursor.fetchall()
        )



    def restore_generator(self, inventory):

        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE generators
        SET active=1
        WHERE inventory=?
        """,
        (
            inventory,
        ))

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

        # Миграция старых баз:
        # если таблица топлива создана раньше без inventory,
        # добавляем недостающее поле
        try:
            cursor.execute(
                "ALTER TABLE fuel_income ADD COLUMN inventory TEXT"
            )
            self.conn.commit()
        except sqlite3.OperationalError:
            pass



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





    def create_fuel_distribution_table(self):
        cursor=self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fuel_distribution(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory TEXT,
            date TEXT,
            liters REAL DEFAULT 0,
            manual INTEGER DEFAULT 0
        )
        """)

        try:
            cursor.execute(
                "ALTER TABLE fuel_distribution ADD COLUMN manual INTEGER DEFAULT 0"
            )
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

        self.conn.commit()

    def clear_fuel_distribution(self, date):
        self.conn.execute("DELETE FROM fuel_distribution WHERE date=?", (date,))
        self.conn.commit()

    def add_fuel_distribution(self, inventory, date, liters, manual=0):
        self.conn.execute(
            "INSERT INTO fuel_distribution(inventory,date,liters,manual) VALUES(?,?,?,?)",
            (inventory,date,liters,manual)
        )
        self.conn.commit()

    def get_fuel_distribution(self, start_date=None, end_date=None):
        cur=self.conn.cursor()
        if start_date and end_date:
            cur.execute(
                "SELECT inventory as generator,date,liters,manual FROM fuel_distribution WHERE date BETWEEN ? AND ? ORDER BY date,inventory",
                (start_date,end_date)
            )
        else:
            cur.execute(
                "SELECT inventory as generator,date,liters,manual FROM fuel_distribution ORDER BY date,inventory"
            )
        return self._rows_to_dicts(cur.fetchall())


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




    def get_start_balance(
            self,
            inventory,
            year,
            month,
            decade,
            first_work_date
        ):
        generator = self.get_generator(inventory)
        if generator:
            initial = float(generator.get("initial_balance") or 0)
            if initial > 0:
                return initial
            template = generator.get("template")
            if template:
                try:
                    from app.services.excel_reader import read_start_balance
                    balance = read_start_balance(template, decade, first_work_date)
                    if balance is not None:
                        return balance
                except Exception:
                    pass
        if hasattr(first_work_date, "strftime"):
            d = first_work_date.strftime("%Y-%m-%d")
        else:
            d = str(first_work_date)
        return self.get_last_balance(inventory, d)

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


        result = []

        for row in cursor.fetchall():

            inventory = row["inventory"]

            # проверяем, что генератор существует
            cursor2 = self.conn.cursor()

            cursor2.execute("""
            SELECT status
            FROM generators
            WHERE inventory=?
            """,
            (inventory,))


            gen = cursor2.fetchone()


            if gen:

                # если в карточке нерабочий -
                # исключаем
                if gen["status"] == "Нерабочий":
                    continue


                result.append(
                    inventory
                )


        return result

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