from typing import List

from pydantic import BaseModel, validator


class AircraftSC(BaseModel):
    aircraftCode: str = None
    seats: int = 0


class FlightSC(BaseModel):
    fromAirport: str
    toAirport: str
    price: float
    start_time: int
    end_time: int

    @validator('end_time')
    def end_time_must_be_greater_that_start_time(cls, end_time, values,  **kwargs):
        if values['start_time'] < end_time:
            return end_time
        raise ValueError('end_time should be greater than start_time')


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

    @validator('departureItineraryArray', 'returnItineraryArray')
    def non_empty_list(cls, value,  **kwargs):
        if isinstance(value, list) and len(value) > 0:
            return value
        raise ValueError('Itinerary array cannot be empty')


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
