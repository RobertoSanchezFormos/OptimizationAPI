from typing import List

from pydantic import BaseModel, validator


class ORMBaselModel(BaseModel):
    class Config:
        orm_mode = True


class AircraftSC(ORMBaselModel):
    aircraftCode: str = None
    seats: int = 0


class FlightSC(ORMBaselModel):
    fromAirport: str
    toAirport: str
    price: float
    timeInMin: int

    @validator('timeInMin')
    def time_in_min_must_be_greater_equal_to_zero(cls, time_in_min, **kwargs):
        if time_in_min >= 0:
            return time_in_min
        raise ValueError('timeInMin should be greater or equal to zero')


class ProcessedItinerarySC(ORMBaselModel):
    key: str
    segmentStart: int
    segmentEnd: int
    preReposition: FlightSC
    trip: FlightSC
    posReposition: FlightSC


class ProcessedAircraftDataSC(ORMBaselModel):
    departureItineraryArray: List[ProcessedItinerarySC]
    returnItineraryArray: List[ProcessedItinerarySC]
    processedAircraft: AircraftSC

    @validator('departureItineraryArray', 'returnItineraryArray')
    def non_empty_list(cls, value, **kwargs):
        if isinstance(value, list) and len(value) > 0:
            return value
        raise ValueError('Itinerary array cannot be empty')


class CalendarInformationSC(ORMBaselModel):
    processedAircraftData: List[ProcessedAircraftDataSC]


class MinCostRoundTripAnswerSC(ORMBaselModel):
    isSuccess: bool = False
    msg: str = ''
    departureAircraft: str = ''
    returnAircraft: str = ''
    price: str = ''
    isSameSegmentOrContinuous: bool = False
    departurePath: ProcessedItinerarySC
    returnPath: ProcessedItinerarySC
