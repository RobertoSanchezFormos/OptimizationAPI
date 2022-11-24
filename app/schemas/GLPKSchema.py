from typing import List

from pydantic import BaseModel


class AircraftSC(BaseModel):
    aircraftCode: str = None
    seats: int = 0


class FlightSC(BaseModel):
    fromAirport: str
    toAirport: str
    price: float
    start_time: int
    end_time: int


class ProcessedItinerarySC(BaseModel):
    key: str
    segmentStart: int
    segmentEnd: int
    preReposition: FlightSC
    trip: FlightSC
    posReposition: FlightSC


class ProcessedAircraftDataSC(BaseModel):
    departureItineraryArray: List[ProcessedItinerarySC]
    returnItineraryArray: List[ProcessedItinerarySC]
    processedAircraft: AircraftSC


class CalendarInformationSC(BaseModel):
    processedAircraftData: List[ProcessedAircraftDataSC]


class MinCostRoundTripAnswerSC(BaseModel):
    isSuccess: bool = False
    msg: str = ''
    departureAircraft: str = ''
    returnAircraft: str = ''
    price: str = ''
    isSameSegment: bool = ''
    departurePath: ProcessedItinerarySC
    returnPath: ProcessedItinerarySC
