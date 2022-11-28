from typing import List, Self
from modeling.classes.Flight import Flight


class ProcessedItinerary:
    key: str = None
    segmentStart: int = None
    segmentEnd: int = None
    preReposition: Flight = None
    trip: Flight = None
    posReposition: Flight = None
    segmentTimeInMin: int = None
    nextPossibleSegments: List[str] = list()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if isinstance(self.preReposition, dict):
            self.preReposition = Flight(**self.preReposition)
        if isinstance(self.trip, dict):
            self.trip = Flight(**self.trip)
        if isinstance(self.posReposition, dict):
            self.posReposition = Flight(**self.posReposition)
        if self.segmentEnd - self.segmentStart > 0:
            self.segmentTimeInMin = self.segmentEnd - self.segmentStart
        else:
            raise Exception(f"Invalid object for Processed Itinerary: segmentTimeInMin must be greater than zero, "
                            f"this means: segmentEnd - segmentStart > 0"
                            f"{self.segmentEnd} - {self.segmentStart} = "
                            f"{self.segmentEnd - self.segmentStart}")

    def preTripPrice(self, ):
        return self.preReposition.price + self.trip.price

    def tripPosPrice(self, ):
        return self.trip.price + self.posReposition.price

    def preTripPosPrice(self, ):
        return self.preReposition.price + self.trip.price + self.posReposition.price

    def preTripTimeInMin(self, ):
        return self.preReposition.timeInMin + self.trip.timeInMin

    def tripPosTimeInMin(self, ):
        return self.trip.timeInMin + self.posReposition.timeInMin

    def preTripPosTimeInMin(self, ):
        return self.preReposition.timeInMin + self.trip.timeInMin + self.posReposition.timeInMin

    def isNextPossibleSegmentOf(self, to_evaluate: Self):
        return self.key in to_evaluate.nextPossibleSegments

    def __str__(self, ):
        return f'..{str(self.key)[-3:]}: {self.preReposition} {self.trip} {self.posReposition} : ' \
               f'({round(self.segmentStart, 0)}, {round(self.segmentEnd, 0)}) ' \
               f'= {round(self.preTripPosPrice(), 2)}'

    def to_dict(self):
        return dict(key=self.key, segmentStart=self.segmentStart, segmentEnd=self.segmentEnd,
                    preReposition=self.preReposition.to_dict() if self.preReposition is not None else dict(),
                    trip=self.trip.to_dict() if self.trip is not None else dict(),
                    posReposition=self.posReposition.to_dict() if self.posReposition is not None else dict())
