from pydantic import Field, BaseModel, ConfigDict, model_validator
import httpx, typing
from . import Products
from datetime import datetime, timezone, timedelta

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from typing import Optional



class APIModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        arbitrary_types_allowed=True
    )



class Location(APIModel):
    latitude: float = Field(alias="latitude")
    longitude: float = Field(alias="longitude")


class StopBase(APIModel):
    evaNumber: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    canceled: Optional[bool] = Field(default=None)
    additional: Optional[bool] = Field(default=None)
    separation: Optional[bool] = Field(default=None)
    slug: Optional[str] = Field(default=None)
    displayPriority: Optional[int] = Field(default=None)
    nameParts: Optional[list] = Field(default=None)

    def __post_init__(self):
        self.id = self.evaNumber


class StopPlace(StopBase): pass

class Destination(StopBase): pass

class Stop(StopBase): pass


class Message(APIModel):
    text: str = Field(alias="text")
    type: str = Field(alias="type")
    change: bool = Field(alias="change")
    important: bool = Field(alias="important")


class DepArrBase(APIModel):
    station_id: str = Field(alias="bahnhofsId", default="")
    time: datetime = Field(alias="zeit", default="")
    time_delayed: datetime = Field(alias="ezZeit", default=None)
    planed_platform: str = Field(alias="gleis", default="")
    platform: str = Field(alias="ezGleis", default="")
    via: typing.List[str] = Field(alias="ueber", default=[])
    journey_id: str = Field(alias="journeyId", default="")
    line_name: str = ""
    end_station: str = Field(alias="terminus", default="")
    station_name: str = Field(alias="station_name", default="")

    @model_validator(mode="before")
    @classmethod
    def extract_line_name(cls, data):
        if isinstance(data, dict):
            data = data.copy()
            data["line_name"] = data.get("verkehrmittel", {}).get("mittelText", "")
        return data

    def export(self):
        styles = getSampleStyleSheet()
        story = []
        class_ = self.__class__.__name__

        filename = f"{class_}_{self.station_name}.pdf"
        story.append(Paragraph(f"{class_}s board", styles["Title"]))
        data = [["Time", "Delayed", "Line", "To", "Platform"]]

        story.append(Paragraph(self.station_name, styles['Heading2']))
        story.append(Spacer(1, 12))

        from .. import PyBahn
        
        departures: list[DepArrBase] = getattr(PyBahn(), f"{class_.lower()}s")(self.station_name)

        doc = SimpleDocTemplate(filename, pagesize=A4)

        # Title
        story.append(Spacer(1, 0.2 * inch))

        # Fill table rows
        for dep in departures:
            time_str = dep.time.strftime("%H:%M")
            delayed_str = dep.time_delayed.strftime("%H:%M") if dep.time_delayed else "-"
            platform_str = dep.platform if dep.platform else dep.planed_platform

            data.append([
                time_str,
                delayed_str,
                dep.line_name,
                dep.end_station,
                platform_str
            ])

        # Create the table
        table = Table(data, repeatRows=1)

        # Style the table
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))

        story.append(table)
        doc.build(story)
        return filename

class Departure(DepArrBase): ...

class Arrival(DepArrBase): ...


class Station(APIModel):
    name: str
    id: str
    lid: str
    stopover_time: int = 0
    location: Location
    products: list[Products] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def parse_location(cls, data):
        data = data.copy()

        data["location"] = Location(
            latitude=data.pop("lat", 0),
            longitude=data.pop("lon", 0),
        )

        return data

class Operator(APIModel):
    id: int = Field(alias="code", default=0)
    has_shop: bool = Field(alias="hatShop", default=False)
    code: str = Field(alias="kuerzel", default="")
    description: str | None
    logo: str | None
    short_description: str = Field(alias="shortDescription", default="")


class J_StopOver(APIModel):
    id: str = Field(alias="id", default=None)
    departure_time: str = Field(alias="abfahrtsZeitpunkt", default=None)
    arrival_time: str = Field(alias="ankunftsZeitpunkt", default=None)
    platform: str = Field(alias="gleis", default=None)
    station_name: str = Field(alias="name", default=None)
    station_id: str = Field(alias="extId", default=None)
    #self.himMeldungen = himMeldungen
    #self.routeIdx = routeIdx
    #self.priorisierteMeldungen = priorisierteMeldungen
    #self.auslastungsmeldungen = auslastungsmeldungen # Кол. Людей
    #self.risNotizen: list = risNotizen
    #self.bahnhofsInfoId: str = bahnhofsInfoId
    #self.haltTyp: str = haltTyp

class info_of_mean_of_transport(APIModel):
    pass


class J_means_of_transport(APIModel):
    name: str = Field(alias="name", default="")
    transport_way_id: str = Field(alias="nummer", default="")
    direction: str = Field(alias="richtung", default="")
    info: typing.List[info_of_mean_of_transport] = []
    short_name: str = Field(alias="kurzText", default="")
    middle_name: str = Field(alias="mittelText", default="")
    full_name: str = Field(alias="langText", default="")

class Connection(APIModel):
    """
    Represents a leg of a journey, containing details such as departure and arrival times and stations,
    the means of transport used, and a list of intermediate stopovers.

    Attributes:
        departure_time (str): Scheduled departure time.
        arrival_time (str): Scheduled arrival time.
        departure_station (str): Name of the departure station.
        arrival_station (str): Name of the arrival station.
        stopovers (List[J_StopOver]): Intermediate stops during the connection.
        journeyId (str): Identifier for the journey leg.
        means_of_transport (J_means_of_transport): Transport method used for the connection.
    """
    departure_time: str = Field(alias="abfahrtsZeitpunkt", default=None)
    departure_station: str = Field(alias="abfahrtsOrt", default=None)
    departure_delay: str = Field(alias="ezAbfahrtsZeitpunkt", default=None)
    arrival_time: str = Field(alias="ankunftsZeitpunkt", default=None)
    arrival_station: str = Field(alias="ankunftsOrt", default=None)
    stopovers: typing.List[J_StopOver] = []
    journeyId: str = Field(alias="journeyId", default=None)
    means_of_transport: J_means_of_transport = None
    #self.iceSprinterNote = iceSprinterNote
    #self.abfahrtsOrtExtId = abfahrtsOrtExtId
    #self.abschnittsDauer = abschnittsDauer
    #self.abschnittsAnteil = abschnittsAnteil
    #self.ezAbschnittsDauerInSeconds = ezAbschnittsDauerInSeconds
    #self.risNotizen = risNotizen
    #self.himMeldungen = himMeldungen
    #self.priorisierteMeldungen = priorisierteMeldungen
    #self.externeBahnhofsinfoIdOrigin = externeBahnhofsinfoIdOrigin
    #self.externeBahnhofsinfoIdDestination = externeBahnhofsinfoIdDestination
    #self.ankunftsOrtExtId = ankunftsOrtExtId
    #self.auslastungsmeldungen = auslastungsmeldungen
    #self.idx = idx


class Coordinates(APIModel):
    longitude: float = Field(alias="lng", default=None)
    latitude: float = Field(alias="lat", default=None)


class Polyline(APIModel):
    coordinates: list[Coordinates] = Field(default_factory=list, alias="coordinates")
    delta: bool = Field(default=False, alias="delta")


class Journey(APIModel):
    """
    Represents a full journey from a departure station to a destination, including all connections.

    Attributes:
        trip_lid (str): Context-based ID for this journey.
        changes_amont (int): Number of transfers during the journey.
        departure_name (str): Name of the departure station.
        arrival_name (str): Name of the destination station.
        connections (List[Connection]): List of connections (legs) within the journey.
        journey_time_in_seconds (int): Estimated journey duration in seconds.
        is_alternative_connection (bool): Whether this is an alternative route.
        preis (str): Ticket price, if available.
    """
    def __init__(self, tripId = None, ctxRecon = None, verbindungsAbschnitte = None, umstiegsAnzahl = None, verbindungsDauerInSeconds = None, ezVerbindungsDauerInSeconds = None, isAlternativeVerbindung = None, auslastungsmeldungen = None, auslastungstexte = None, himMeldungen = None, risNotizen = None, priorisierteMeldungen = None, reservierungsMeldungen = None, isAngebotseinholungNachgelagert = None, isAlterseingabeErforderlich = None, serviceDays = None, angebotsPreis = None, angebotsPreisKlasse = None, hasTeilpreis = None, reiseAngebote = None, hinRueckPauschalpreis = None, isReservierungAusserhalbVorverkaufszeitraum = None, gesamtAngebotsbeziehungList = None, ereignisZusammenfassung = None, meldungen = None, meldungenAsObject = None, angebotsInformationen = None, angebotsInformationenAsObject = None, abPreisInfo: dict = None, **kwargs):
        ...
    trip_lid: str = Field(alias="ctxRecon", default=None)
    changes_amont: int = Field(alias="umstiegsAnzahl", default=None)
    departure_name: any = Field(alias="verbindungsAbschnitte", default=None)
    arrival_name: any = Field(alias="verbindungsAbschnitte", default=None)
    connections: typing.List[Connection] = []
    departure_time: str = ""
    arrival_time: str = ""
    #journey_time_in_seconds: int = Field(alias="verbindungsDauerInSeconds", default=None)
    #is_alternative_connection: bool = Field(alias="isAlternativeVerbindung", default=None)
    #additional_messages: typing.Optional[list[str]] = Field(alias="meldungen", default=None)
    #abPreisInfo: typing.Optional[str] = Field(alias="abPreisInfo", default=None)
    #price: str = ""
    #price_without_sale: str = ""
    #self.auslastungsmeldungen = auslastungsmeldungen
    #self.journey_time_in_seconds_e: int = ezVerbindungsDauerInSeconds
    #self.angebotsPreisKlasse: str = angebotsPreisKlasse
    #self.hasTeilpreis: bool = hasTeilpreis
    #self.reiseAngebote = reiseAngebote
    #self.angebotsInformationen = angebotsInformationen
    #self.angebotsInformationenAsObject = angebotsInformationenAsObject
    #self.hinRueckPauschalpreis: bool = hinRueckPauschalpreis
    #self.isReservierungAusserhalbVorverkaufszeitraum: bool = isReservierungAusserhalbVorverkaufszeitraum
    #self.gesamtAngebotsbeziehungList = gesamtAngebotsbeziehungList
    #self.meldungenAsObject = meldungenAsObject
    #self.isAngebotseinholungNachgelagert: bool = isAngebotseinholungNachgelagert
    #self.isAlterseingabeErforderlich: bool = isAlterseingabeErforderlich
    #self.serviceDays = serviceDays
    #self.himMeldungen = himMeldungen
    #self.risNotizen = risNotizen
    #self.priorisierteMeldungen = priorisierteMeldungen
    #self.reservierungsMeldungen = reservierungsMeldungen
    #self.tripId: str = tripId
    
    def get_db_link(self):
        """Returns a link compatible with `DB Navigator` and [int.bahn.de](https://int.bahn.de) """
        url = "https://int.bahn.de/web/api/angebote/verbindung/teilen"
        name_1 = self.departure_name
        name_2 = self.arrival_name
        if self.connections[0].departure_time:
            ti = self.connections[0].departure_time
            dt = datetime.strptime(ti, "%Y-%m-%dT%H:%M:%S")
            time_ = dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        else:
            time_ = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')

        ctx = self.trip_lid

        r = httpx.Client().post(url, json={
            "startOrt": name_1,
            "zielOrt": name_2,
            "hinfahrtDatum": time_,
            "hinfahrtRecon": ctx
        }, headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Accept": "application/json"
        })

        if i := r.json()['vbid']:
            link = "https://int.bahn.de/en/buchung/start?vbid=" + i

            return link
        
        else:
            raise ValueError(r.text)
    
    def export(self):        
        filename = f"journey_{self.departure_name}_{self.arrival_name}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph(f"<b>{self.departure_name} → {self.arrival_name}</b>", styles["Title"]))

            # Journey info
        duration = str(timedelta(seconds=self.journey_time_in_seconds))
        info = (
            f"<b>Departure:</b> {datetime.fromisoformat(self.departure_time).strftime("%a %d. %b, %H:%M")}<br/>"
            f"<b>Arrival:</b> {datetime.fromisoformat(self.arrival_time).strftime("%a %d. %b, %H:%M")}<br/>"
            f"<b>Duration:</b> {duration}<br/>"
            f"<b>Changes:</b> {self.changes_amont or 0}<br/>"
            f"<b>Price:</b> {self.preis or 'N/A'}"
        )
        story.append(Paragraph(info, styles["Normal"]))
        story.append(Spacer(1, 0.3 * inch))

        # Each connection in free style
        for idx, conn in enumerate(self.connections, start=1):
            story.append(Paragraph(f"<b>{conn.departure_station}</b>", styles["Heading3"]))
            story.append(Spacer(1, 0.2 * inch))

            dep_time = conn.departure_time
            arr_time = conn.arrival_time
            try:
                dep_time = datetime.fromisoformat(dep_time).strftime("%H:%M")
            except:
                dep_time = "null"
            try:
                arr_time = datetime.fromisoformat(arr_time).strftime("%H:%M")
            except:
                arr_time = "null"

            line_name = getattr(conn.means_of_transport, "full_name", "Unknown")
            platform = getattr(conn.stopovers[0], "platform", "-") if conn.stopovers else "-"

            details = (
                f"      <b>Line:</b> {line_name}<br/>"
                f"      <b>Departure:</b> {dep_time}<br/>"
                f"      <b>Platform:</b> {platform}<br/>"
                f"      <b>Direction:</b> {conn.means_of_transport.direction}<br/>"
                f"      <b>Arrival:</b> {arr_time}<br/>"
            )
            story.append(Paragraph(details, styles["Normal"]))
            if idx == len(self.connections):
                story.append(Paragraph(f"<b>{conn.arrival_station}</b>", styles["Heading3"]))
            story.append(Spacer(1, 0.2 * inch))

        doc.build(story)
        return filename