from pybahn import PyBahn


bahn = PyBahn()

berlin = bahn.station("Berlin hbf")
print(berlin.name)
print(berlin.id)