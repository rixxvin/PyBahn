from enum import StrEnum, Enum
from datetime import datetime
from typing import List, Literal, Union


class Date:
    def __init__(self):
        self.__date = datetime.now()

    def set_time(self, hour: int, minute: int):
        if 0 <= hour < 24 and 0 <= minute < 60:
            self.__date = self.__date.replace(hour=hour, minute=minute)
        else:
            raise ValueError("Invalid hour or minute")
        
        return self

    def set_date(self, month: int, day: int):
        """You can change only month and day, year is always - current"""
        if 1 <= month <= 12 and 1 <= day <= 31:
            self.__date = self.__date.replace(month=month, day=day)
        else:
            raise ValueError("Invalid month or day")
        
        return self

    def get(self, timespec: Union[str, None] = None) -> str:
        """returns a date as iso format"""
        if timespec:
            return self.__date.replace(second=0, microsecond=0).isoformat(timespec=timespec)
        else:
            return self.__date.replace(second=0, microsecond=0).isoformat()




class Filter(StrEnum):
    """
    ``Example of use``::
    
        from pybahn import PyBahn
        from pybahn.structs import Filter

        client = PyBahn()

        station = client.station("Frankfurt")
        departures = client.departures(id=station, filters=[Filter.TRAM])

        print(departures[0].canceled)

    or 
    ::
        departures = client.departures(id=station, filters=[Filter.TRAM])
    or 
    ::
        filters = Filter.from_list(["S", "U"])
        departures = client.departures(id=station, filters=filters)
    """
    ICE = "&verkehrsmittel[]=ICE"
    IC = "&verkehrsmittel[]=EC_IC"
    FLX = "&verkehrsmittel[]=IR"
    RB_RE = "&verkehrsmittel[]=REGIONAL"
    S = "&verkehrsmittel[]=SBAHN"
    U = "&verkehrsmittel[]=UBAHN"
    BUS = "&verkehrsmittel[]=BUS"
    TRAM = "&verkehrsmittel[]=TRAM"
    RUF = "&verkehrsmittel[]=ANRUFPFLICHTIG"
    BOAT = "&verkehrsmittel[]=SCHIFF"

    ALL = "&verkehrsmittel[]=ICE&verkehrsmittel[]=EC_IC&verkehrsmittel[]=IR&verkehrsmittel[]=REGIONAL&verkehrsmittel[]=SBAHN&verkehrsmittel[]=UBAHN&verkehrsmittel[]=BUS&verkehrsmittel[]=TRAM&verkehrsmittel[]=ANRUFPFLICHTIG&verkehrsmittel[]=SCHIFF"
    REGIONALS = "&verkehrsmittel[]=REGIONAL&&verkehrsmittel[]=SBAHN&verkehrsmittel[]=UBAHN&verkehrsmittel[]=BUS&verkehrsmittel[]=TRAM&verkehrsmittel[]=ANRUFPFLICHTIG&verkehrsmittel[]=SCHIFF"
    HIGH_SPEED = "&verkehrsmittel[]=ICE&verkehrsmittel[]=EC_IC&verkehrsmittel[]=IR"

    @staticmethod
    def from_list(filters: List[Literal["ICE", "IC", "FLX", "RB_RE", "S", "U", "BUS", "TRAM", "RUF", "BOAT", "ALL", "REGIONALS", "HIGH_SPEED"]]) -> List["Filter"]:
        filtered = set(filters)

        result = []
        for name in filtered:
            if name in Filter.__members__:
                result.append(Filter[name])
            else:
                raise ValueError(f"Unknown filter: {name}")
        return result


class Products(Enum):
    """
    ``Example of use``::
    
        from pybahn import PyBahn
        from pybahn.structs import Products

        client = PyBahn()

        station1 = client.station("Frankfurt")
        station2 = client.station("Berlin")
        
        journeys = client.journeys(station1, station2, products=[Products.REGIONAL])

        print(journeys[0])
    """
    ICE = "ICE"
    EC_IC = "EC_IC"
    IR = "IR"
    REGIONAL = "REGIONAL"
    SBAHN = "SBAHN"
    UBAHN = "UBAHN"
    BUS = "BUS"
    TRAM = "TRAM"
    RUF = "ANRUFPFLICHTIG"
    
    REGIONALS = ["REGIONAL", "SBAHN", "UBAHN", "BUS", "TRAM", "ANRUFPFLICHTIG"]
    ALL = ["ICE", "EC_IC", "IR", "REGIONAL", "SBAHN", "UBAHN", "BUS", "TRAM", 'ANRUFPFLICHTIG']
    
    @staticmethod
    def from_list(products: List[Literal["ICE", "EC_IC", "REGIONAL", "SBAHN", "UBAHN", "BUS", "TRAM", "RUF", "ALL", "REGIONALS"]]) -> List["Products"]:
        filtered = set(products)

        result = []
        for name in filtered:
            if name in Products.__members__:
                result.append(Products[name])
            else:
                raise ValueError(f"Unknown product: {name}")
        return result

__all__ = ["Products", "Filter", "Date"]