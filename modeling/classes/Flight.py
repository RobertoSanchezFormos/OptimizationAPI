class Flight:
    fromAirport: str = None
    toAirport: str = None
    price: float = None
    start_time: int = None
    end_time: int = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self, ):
        return f'({round(self.start_time,0)},{round(self.end_time,0)}) {self.fromAirport} -> ' \
               f'{self.toAirport}: {round(self.price, 2)} | '