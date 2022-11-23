class Aircraft:
    aircraftCode: str = None
    seats: int = 0

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self, ):
        return f'({self.aircraftCode}: {self.seats})'
