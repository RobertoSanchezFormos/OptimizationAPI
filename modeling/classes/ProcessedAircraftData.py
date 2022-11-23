from typing import List

from modeling.classes.Aircraft import Aircraft
from modeling.classes.ProcessedItinerary import ProcessedItinerary


class ProcessedAircraftData:
    departureItineraryArray: List[ProcessedItinerary] = list()
    returnItineraryArray: List[ProcessedItinerary] = list()
    processedAircraft: Aircraft = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.departureItineraryArray = list()
        self.returnItineraryArray = list()
