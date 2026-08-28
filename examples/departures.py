from pybahn import PyBahn
from pybahn.structs import Filter, Date


bahn = PyBahn()


berlin = bahn.station("Frankfurt hbf")

date = Date().set_time(hour=12, minute=00).set_date(month=12, day=2)

filters = Filter.from_list(["S", "U", "TRAM"])


departures = bahn.departures(berlin, filters=filters, date=date, limit=2)
for dep in departures:
    print("="*15)
    print(f"""line: {dep.line_name}
platform: {dep.platform}
time: {dep.time.hour}:{dep.time.minute}
    """)