from modeling.classes.Flight import Flight


class ProcessedItinerary:
    key: str = None
    segmentStart: int = None
    segmentEnd: int = None
    preReposition: Flight = None
    trip: Flight = None
    posReposition: Flight = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def preTripPrice(self, ):
        return self.preReposition.price + self.trip.price

    def tripPosPrice(self, ):
        return self.trip.price + self.posReposition.price

    def preTripPosPrice(self, ):
        return self.preReposition.price + self.trip.price + self.posReposition.price

    def __str__(self, ):
        return f'{self.key}: {self.preReposition} {self.trip} {self.posReposition} : ' \
               f'({round(self.segmentStart, 2)}, {round(self.segmentEnd, 2)}) '
