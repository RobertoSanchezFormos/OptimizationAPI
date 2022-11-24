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
        if len(self.departureItineraryArray) > 0 and isinstance(self.departureItineraryArray[0], dict):
            self.departureItineraryArray = [ProcessedItinerary(**d) for d in self.departureItineraryArray]
        if len(self.returnItineraryArray) > 0 and isinstance(self.returnItineraryArray[0], dict):
            self.returnItineraryArray = [ProcessedItinerary(**d) for d in self.returnItineraryArray]
        if isinstance(self.processedAircraft, dict):
            self.processedAircraft = Aircraft(**self.processedAircraft)

    def __str__(self, ):
        dep = '\n'.join(str(x) for x in self.departureItineraryArray)
        back = '\n'.join(str(x) for x in self.returnItineraryArray)
        return f"departure:\n{dep} \nreturn:\n{back}"
