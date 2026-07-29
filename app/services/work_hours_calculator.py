class WorkHoursCalculator:
    """
    Расчет часов работы генератора по топливу.

    Правила:
    - остаток переносится между днями;
    - максимум 8 часов в сутки;
    - расход берется из генератора, по умолчанию 2.5 л/ч.
    """

    def __init__(self, default_consumption=2.5, max_hours=8):
        self.default_consumption = default_consumption
        self.max_hours = max_hours


    def calculate_day(self, start_balance, received_fuel, consumption=None):
        consumption = float(consumption or self.default_consumption)

        if consumption <= 0:
            consumption = self.default_consumption

        available = float(start_balance or 0) + float(received_fuel or 0)

        if available < 0:
            raise ValueError(
                "Отрицательный остаток топлива"
            )

        hours = available / consumption

        if hours > self.max_hours:
            hours = self.max_hours

        hours = round(hours, 1)

        used_fuel = hours * consumption

        end_balance = available - used_fuel

        if end_balance < 0:
            end_balance = 0

        return {
            "hours": hours,
            "used_fuel": round(used_fuel, 2),
            "balance": round(end_balance, 2)
        }


    def calculate_period(self, days, start_balance, consumption=None):
        result = []

        balance = float(start_balance or 0)

        for day in days:
            calc = self.calculate_day(
                balance,
                day.get("received", 0),
                consumption
            )

            result.append({
                "date": day.get("date"),
                "hours": calc["hours"],
                "received": day.get("received", 0),
                "balance": calc["balance"]
            })

            balance = calc["balance"]

        return result
