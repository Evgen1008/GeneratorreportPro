from app.database import Database
from app.services.fuel_calculator import FuelCalculator


db = Database()
print("ТОПЛИВО В БАЗЕ:")
for row in db.get_fuel_income():
    print(row["date"], row["liters"])

calculator = FuelCalculator(db)
print("ТОПЛИВО:")
for row in db.get_fuel_income():
    print(
        row["date"],
        row["liters"]
    )

print("----------------")

result = calculator.calculate_decade(
    2026,
    7,
    1
)


for row in result:
    print(row)


db.close()
print("Количество записей:", len(result))

print("---------------------")

for row in result[:10]:
    print(
        row["date"],
        row["inventory"],
        "часов:",
        row["hours"],
        "расход:",
        row["fuel_used"],
        "остаток:",
        row["balance"]
    )
   