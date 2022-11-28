from pydantic.main import BaseModel

from modeling.classes.ProcessedItinerary import ProcessedItinerary


class MinCostRoundTripAnswer:
    isSuccess: bool = False
    msg: str = ''
    departureAircraft: str = ''
    returnAircraft: str = ''
    price: str = ''
    isSameSegmentOrContinuous: bool = False
    departurePath: ProcessedItinerary = ProcessedItinerary()
    returnPath: ProcessedItinerary = ProcessedItinerary()

    def to_dict(self):
        return dict(isSuccess=self.isSuccess, msg=self.msg, departureAircraft=self.departureAircraft,
                    returnAircraft=self.returnAircraft, price=self.price,
                    isSameSegmentOrContinuous=self.isSameSegmentOrContinuous,
                    departurePath=self.departurePath.to_dict(),
                    returnPath=self.returnPath.to_dict())

    def __str__(self, ):
        return f'(success: {self.isSuccess}) {self.msg if not self.isSuccess else ""} ' \
               f'Aircrafts:(-> dep: {self.departureAircraft}, <- ret: {self.returnAircraft}) ' \
               f'isSameSegmentOrContinuous: {self.isSameSegmentOrContinuous} ' \
               f'\nPrice: {self.price} \n' \
               f'departurePath:  {self.departurePath}\n' \
               f'returnPath:  {self.returnPath}\n'
