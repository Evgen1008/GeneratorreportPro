from datetime import date, timedelta
import calendar
import math


class FuelCalculator:

    MAX_HOURS = 8
    FUEL_STEP = 5

    def __init__(self, database):
        self.db = database

    def get_decade_dates(self, year, month, decade):
        last_day = calendar.monthrange(year, month)[1]
        if decade == 1:
            return date(year, month, 1), date(year, month, 10)
        if decade == 2:
            return date(year, month, 11), date(year, month, 20)
        if decade == 3:
            return date(year, month, 21), date(year, month, last_day)
        raise ValueError("Неверная декада")

    def get_fuel_for_day(self, day):
        total = 0
        for row in self.db.get_fuel_income():
            if row["date"] in [str(day), day.strftime("%d.%m.%Y")]:
                total += float(row["liters"] or 0)
        return total

    def distribute_fuel(self, received, generators, balances):
        result = {g["inventory"]: 0 for g in generators}

        if received < self.FUEL_STEP:
            return result

        needs = {}
        total_need = 0

        for gen in generators:
            inv = gen["inventory"]
            cons = float(gen["consumption"] or 0)
            need = max(0.0, cons * self.MAX_HOURS - float(balances.get(inv, 0)))
            needs[inv] = need
            total_need += need

        distributed = 0

        for gen in generators:
            inv = gen["inventory"]
            if total_need > 0:
                share = received * needs[inv] / total_need
            else:
                share = 0

            fuel = int(share // self.FUEL_STEP) * self.FUEL_STEP
            result[inv] = fuel
            distributed += fuel

        remainder = received - distributed

        while remainder >= self.FUEL_STEP:
            candidates = [
                g for g in generators
                if result[g["inventory"]] + self.FUEL_STEP <= needs[g["inventory"]] + self.FUEL_STEP
            ]

            if not candidates:
                break

            target = max(
                candidates,
                key=lambda g: needs[g["inventory"]] - result[g["inventory"]]
            )

            result[target["inventory"]] += self.FUEL_STEP
            remainder -= self.FUEL_STEP

        return result

    def calculate_decade(self, year, month, decade):

        start_date, end_date = self.get_decade_dates(year, month, decade)

        generators = self.db.get_generators()

        balances = {}

        for gen in generators:
            inventory = gen["inventory"]
            balances[inventory] = self.db.get_start_balance(
                inventory,
                year,
                month,
                decade,
                start_date
            )

        results = []

        current = start_date

        while current <= end_date:

            received = self.get_fuel_for_day(current)

            # Используем сохранённое распределение топлива из окна
            # распределения (авто или ручное), а не пересчитываем заново.
            saved_distribution = self.db.get_fuel_distribution(
                str(current),
                str(current)
            )

            if saved_distribution:
                distribution = {}

                for item in saved_distribution:
                    distribution[item["generator"]] = float(
                        item["liters"] or 0
                    )
            else:
                distribution = self.distribute_fuel(
                    received,
                    generators,
                    balances
                )

            for gen in generators:

                inventory = gen["inventory"]
                consumption = float(gen["consumption"] or 0)

                available = (
                    float(balances.get(inventory, 0))
                    +
                    float(distribution.get(inventory, 0))
                )

                if consumption > 0:
                    hours = int(available / consumption)
                else:
                    hours = 0

                hours = min(hours, self.MAX_HOURS)

                fuel_used = hours * consumption
                balance = available - fuel_used

                if balance < 0:
                    balance = 0

                balance = round(balance, 1)
                balances[inventory] = balance

                row = {
                    "inventory": inventory,
                    "date": current.strftime("%Y-%m-%d"),
                    "received": distribution.get(inventory, 0),
                    "hours": hours,
                    "consumption": consumption,
                    "fuel_used": round(fuel_used, 1),
                    "balance": balance
                }

                results.append(row)

                self.db.save_daily_report(
                    row["inventory"],
                    row["date"],
                    row["received"],
                    row["hours"],
                    row["consumption"],
                    row["fuel_used"],
                    row["balance"]
                )

            current += timedelta(days=1)

        return results
