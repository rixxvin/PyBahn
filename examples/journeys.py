from pybahn import PyBahn
from pybahn.structs import Products, Date
from pybahn.travellers import YOUTH, DOG

bahn = PyBahn()

berlin = bahn.station("Berlin hbf")
frankfurt = bahn.station("Frankfurt")

products = Products.from_list(["ICE"])

date = Date().set_time(hour=2, minute=0).set_date(month=8, day=28)

journeys = bahn.journeys(
    departure=berlin,
    destination=frankfurt,
    date=date,
    products=products,
    only_d_ticket=False,
    stopovers=None,
    travellers=[YOUTH(), DOG()],
    all_passengers_includes_d_ticket=True,
    travel_class=1
)

for id, journey in enumerate(journeys):
    print(f"""
{'='*15} JOURNEY {id} {'='*15}
origin: {journey.connections[0].origin.name}
destination: {journey.connections[-1].destination.name}
{'-'*15}
stopovers amount: {journey.stopovers_amount}
departure time: {journey.connections[0].origin.departure.planned_time}
arrival time: {journey.connections[-1].destination.arrival.planned_time}
    """)
