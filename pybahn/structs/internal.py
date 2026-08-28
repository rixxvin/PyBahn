from pydantic import BaseModel, Field, model_validator, ConfigDict
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from datetime import datetime


class APIModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore"
    )


class Location(APIModel):
    latitude: float
    longitude: float


class Station(APIModel):
    id: str = Field(alias="extId")
    lid: str = Field(alias="id")
    location: Location
    name: str
    products: list[str]

    @model_validator(mode="before")
    @classmethod
    def parse_location(cls, data):
        data = data.copy()

        data["location"] = Location(
            latitude=data.pop("lat", 0),
            longitude=data.pop("lon", 0),
        )

        return data



class DepartureArrivalBase(APIModel):
    station_id: str = Field(alias="bahnhofsId", default="")
    time: datetime = Field(alias="zeit", default="")
    time_delayed: datetime = Field(alias="ezZeit", default=None)
    planed_platform: str = Field(alias="gleis", default="")
    platform: str = Field(alias="ezGleis", default="")
    via: list[str] = Field(alias="ueber", default=[])
    journey_id: str = Field(alias="journeyId", default="")
    line_name: str = ""
    end_station: str = Field(alias="terminus", default="")
    station_name: str

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
        
        departures: list[DepartureArrivalBase] = getattr(PyBahn(), f"{class_.lower()}s")(self.station_name)

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


class Departure(DepartureArrivalBase): ...
class Arrival(DepartureArrivalBase): ...


class Timing(APIModel):
    planned_time: datetime | None = Field(default=None, alias="sollzeit")
    delayed_time: datetime | None = Field(default=None, alias="echtzeit")


class ConectionsStartStation(APIModel):
    id: str = Field(alias="extId")
    name: str
    departure: Timing = Field(alias="abfahrt")


class ConectionsEndStation(APIModel):
    id: str = Field(alias="extId")
    name: str
    arrival: Timing = Field(alias="ankunft")


class Connection(APIModel):
    origin: ConectionsStartStation = Field(alias="startHalt")
    destination: ConectionsEndStation = Field(alias="zielHalt")
    is_destination_cancelled: bool = Field(alias="destinationCancelled")
    is_origin_cancelled: bool = Field(alias="originCancelled")
    stopovers: list[Stopover] = Field(alias="halte")
    transport: Transport = Field(alias="verkehrsmittel")
    

class Stopover(APIModel):
    "Please don't forget that first stopover doesn't include 'arrival', and last one - 'departure'"
    id: str | None
    departure: Timing | None = Field(default=None, alias="abfahrt")
    arrival: Timing | None = Field(default=None, alias="ankunft")
    planned_platform: str | None = Field(default=None, alias="gleis")
    name: str


class Transport(APIModel):
    category: str = Field(alias="kategorie")
    name: str
    direction: str = Field(alias="produktGattung")
    short_text: str = Field(alias="kurzText")
    med_text: str  = Field(alias="mittelText")
    long_text: str = Field(alias="langText")


class Journey(APIModel):
    lid: str = Field(alias="ctxRecon")
    stopovers_amount: int = Field(alias="umstiegsAnzahl")
    is_alternative_connection: bool = Field(alias="isAlternativeVerbindung")
    connections: list[Connection] = Field(alias="verbindungsAbschnitte")
    journey_time_in_seconds: int | None = Field(default=None, alias="verbindungsDauerInSeconds")


class Operator(APIModel):
    id: int = Field(alias="code", default=0)
    has_shop: bool = Field(alias="hatShop", default=False)
    code: str = Field(alias="kuerzel", default="")
    description: str | None
    logo: str | None
    short_description: str = Field(alias="shortDescription", default="")


class Coordinates(APIModel):
    longitude: float = Field(alias="lng", default=None)
    latitude: float = Field(alias="lat", default=None)


class Polyline(APIModel):
    coordinates: list[Coordinates] = Field(default_factory=list, alias="coordinates")
    delta: bool = Field(default=False, alias="delta")