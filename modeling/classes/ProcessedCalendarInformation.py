from typing import List

from modeling.classes.ProcessedAircraftData import ProcessedAircraftData


class ProcessedCalendarInformation:
    processedAircraftData: List[ProcessedAircraftData]

    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)
