from pybahn import PyBahn
from pybahn.structs import Filter, Date

bahn = PyBahn()

berlin = bahn.station("Berlin hbf")
frankfurt = bahn.station("Frankfurt")

filters = Filter.from_list(["S", "U", "BUS"])

date = Date().set_time(12, 00).set_date(10, 2)

berlin_departures = bahn.departures(berlin, filters=filters, date=date)
pdf_path = berlin_departures[0].export()

print(pdf_path)