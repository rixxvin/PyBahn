
# Pybahn

A Python library to query Deutsche Bahn journey, departure, and arrival data using the (unofficial) API.


## 📚 Table of Contents

 - [📦 Installation](#-installation)
 - [🛠️ Usage](#-usage)
 - [🔧 Initialize PyBahn](#-initialize-pybahn)
 - [🔍 Search Stations](#-search-stations)
 - [📍 Get a Single Station](#-get-a-single-station)
 - [🗺️ Nearby Stations](#-nearby-stations)
 - [🚉 Departures](#-departures)
 - [🚉 Arrivals](#-arrivals)
 - [🚆 Journeys](#-journeys)
 - [🎯 Filter Departures/Arrivals](#-filter-departuresarrivals)
 - [🎯 Filter Journeys](#-filter-journeys)
 - [🚆 Stopovers](#-stopovers)
 - [⚠️ License](#-license)
 - [⚠️ Disclaimer](#-disclaimer)
 
## 📦 Installation

```bash
pip install pybahn
```
    
## 🛠️ Usage

###	Initialize PyBahn
```python
from pybahn import PyBahn

bahn = PyBahn()
```


### 🔍 Search Station
```python
stations = bahn.stations("Berlin")

for station in stations:
	print(station.name)
```

### 📍 Get a Single Station

```python
station = bahn.station("Munich")
print(station.name)
```

### 🗺️ Nearby Stations

```python
near_stations = bahn.nearby(latitude=52.5170365, longitude=13.3888599, limit=5)

for station in stations:
	print(station.name)
```

### 🚉 Departures

```python
munich = bahn.station("Munich")
departures = bahn.departures(munich)  # Berlin Hbf

print(departures[0].lineName)
```

### 🚉 Arrivals

```python
station = bahn.station("Munich")

arrivals = bahn.arrivals(station)

print(arrivals[0].lineName)
```


### 🚆 Journeys
```python
station1 = bahn.station("Frankfurt")
station2 = bahn.station("Berlin")

journeys = bahn.journeys(station1, station2)

print(journeys[0].arrival_name)
```


### 🎯 Filter Departures/Arrivals

```python
from pybahn.structs import Filter, Date


berlin = bahn.station("Berlin hbf")
frankfurt = bahn.station("Frankfurt")

date = Date().set_time(hour=12, minute=00).set_date(month=10, day=2)

filters = Filter.from_list(["S", "U", "BUS"])

berlin_departures = bahn.departures(berlin, filters=filters, date=date)
print(berlin_departures[0].line_name)


berlin_arrivals = bahn.arrivals(berlin, filters=filters, date=date)
print(berlin_arrivals[0].line_name)
```


### 🎯 Filter Journeys

```python
from pybahn.structs import Products


station1 = bahn.station("Frankfurt")
station2 = bahn.station("Berlin")

journeys = bahn.journeys(station1, station2, products=Products.REGIONALS)

print(journeys[0].changes_amont)
```

#### or

```python
from pybahn.structs import Products


station1 = bahn.station("Frankfurt")
station2 = bahn.station("Berlin")

journeys = bahn.journeys(
				departure=station2,
				destination=station1,
				products=[Products.EC_IC, Products.REGIONAL]
)

print(journeys[0].changes_amont)
```

### 🚆 Stopovers

```python
from pybahn.structs import Date

station1 = bahn.station("Kassel")
station2 = bahn.station("Berlin")

stopover = bahn.station("frankfurt")
stopover.stopover_time = 5

journeys = bahn.journeys(departure=station1, destination=station2, stopovers=[stopo])


print(journeys)
```

## 📄 License

[MIT License](https://choosealicense.com/licenses/mit/)

## ⚠️ Disclaimer

This library (`pybahn`) is an **unofficial** wrapper around Deutsche Bahn’s internal web APIs, discovered via publicly accessible browser traffic.

- It is **not affiliated with or endorsed by Deutsche Bahn**.
- It uses **undocumented and unsupported endpoints**, which may break or change without notice.
- Use this library **at your own risk**.
- Please respect Deutsche Bahn’s terms of use and avoid abusive behavior.
