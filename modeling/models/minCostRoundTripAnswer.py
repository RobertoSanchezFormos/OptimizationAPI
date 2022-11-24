from pydantic.main import BaseModel

from modeling.classes.ProcessedItinerary import ProcessedItinerary


class MinCostRoundTripAnswer:
    isSuccess: bool = False
    msg: str = ''
    departureAircraft: str = ''
    returnAircraft: str = ''
    price: str = ''
    isSameSegment: bool = ''
    departurePath: ProcessedItinerary
    returnPath: ProcessedItinerary

    def to_dict(self):
        return dict(isSuccess=self.isSuccess, msg=self.msg, departureAircraft=self.departureAircraft,
                    returnAircraft=self.returnAircraft, price=self.price,
                    isSameSegment=self.isSameSegment, departurePath=self.departurePath.to_dict(),
                    returnPath=self.returnPath.to_dict())
