from typing import Literal, Optional



class Traveller:
    def __init__(
        self,
        bahn_card: Optional[Literal[25, 50, 100]] = None,
        travelling_class: Optional[Literal[1, 2]] = None,
    ):
        # --- BahnCard handling ---
        if bahn_card is None:
            self.art = "KEINE_ERMAESSIGUNG"
        elif bahn_card not in (25, 50, 100):
            raise ValueError("BahnCard must be 25, 50 or 100")
        else:
            self.art = f"BAHNCARD{bahn_card}"

        # --- Klasse handling ---
        if travelling_class is None:
            self.klasse = "KLASSENLOS"
        elif travelling_class not in (1, 2):
            raise ValueError("Classe must be 1 or 2")
        else:
            self.klasse = "KLASSE_1" if travelling_class == 1 else "KLASSE_2"

class ADULT(Traveller):
    """
    **Traveller age: 27 - 64.**\n
    **description**: Travellers aged 27 and over can benefit from Sparpreis and Super Sparpreis offers, which are available to people of all ages.
    """
    def __init__(
        self,
        bahn_card: Optional[Literal[25, 50, 100]] = None,
        travelling_class: Optional[Literal[1, 2]] = None,
    ):
        self.typ = "ERWACHSENER"
        super().__init__(bahn_card=bahn_card, travelling_class=travelling_class)


class YOUTH(Traveller):
    """
    **Traveller age: 15 - 26.**\n
    **description**: Travellers aged 15-26 can benefit from special offers. These offers are only available to travellers aged 26 and under. Eligibility is based on the passenger's age on the first day of travel.
    """
    def __init__(
        self,
        bahn_card: Optional[Literal[25, 50, 100]] = None,
        travelling_class: Optional[Literal[1, 2]] = None,
    ):
        self.typ = "JUGENDLICHER"
        super().__init__(bahn_card=bahn_card, travelling_class=travelling_class)


class CHILD(Traveller):
    """
    **Traveller age: 6 - 14.**\n
    **description**: This traveller type is only used internally to calculate the offers for children travelling alone.
    """
    def __init__(
        self,
        bahn_card: Optional[Literal[25, 50, 100]] = None,
        travelling_class: Optional[Literal[1, 2]] = None,
    ):
        self.typ = "FAMILIENKIND"
        super().__init__(bahn_card=bahn_card, travelling_class=travelling_class)


class BICYCLE(Traveller):
    """
    **Bike**\n
    **description**: A standard, single-seat bicycle for adults with two wheels. Information on taking other types of bicycle with you can be found at https://bahn.de/fahrrad.
    """
    def __init__(self):
        self.typ = "FAHRRAD"
        self.art = "KEINE_ERMAESSIGUNG"
        self.klasse = "KLASSENLOS"
        super().__init__(bahn_card=None, travelling_class=None)

class DOG(Traveller):
    """
    **Dog**\n
    **description**: Dogs that are not accommodated in a standard transport box during the journey. Guide/assistance dogs always travel free of charge and do not need to be specified when booking.
    """
    def __init__(self):
        self.typ = "HUND"
        self.art = "KEINE_ERMAESSIGUNG"
        self.klasse = "KLASSENLOS"
        super().__init__(bahn_card=None, travelling_class=None)



__all__ = ["ADULT", "YOUTH", "CHILD", "BICYCLE", "DOG"]