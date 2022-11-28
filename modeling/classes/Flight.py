from pydantic.main import BaseModel


class Flight:
    fromAirport: str = None
    toAirport: str = None
    price: float = None
    timeInMin: int = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self, ):
        return f'({round(self.timeInMin, 0)} min.) {self.fromAirport} -> ' \
               f'{self.toAirport}: {round(self.price, 2)} | '

    def to_dict(self):
        return dict(fromAirport=self.fromAirport,
                    toAirport=self.toAirport,
                    price=self.price,
                    timeInMin=self.timeInMin)
