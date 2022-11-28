import random
from random import randint
from typing import List
from uuid import uuid4
import pandas as pd
import datetime as dt

from modeling.classes.Aircraft import Aircraft
from modeling.classes.Flight import Flight
from modeling.classes.ProcessedAircraftData import ProcessedAircraftData
from modeling.classes.ProcessedItinerary import ProcessedItinerary
from modeling.models.utils import generateParameters, generateDayValidPeriodsPerDay


class ItineraryGenerator:
    seed: int
    airportNames: list
    aircrafts: List[Aircraft] = []
    aircraftNames: list
    time_dict: dict
    cost_dict: dict
    n_days: int
    df_days: pd.DataFrame
    tv_i: int
    tv_f: int

    def __init__(self, aircrafts: List[Aircraft], airport_names: List[str], n_days: int, start_hour: dt.timedelta,
                 end_hour: dt.timedelta, seed, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.seed = seed
        self.aircrafts = aircrafts
        self.airportNames = airport_names
        self.aircraftNames = [a.aircraftCode for a in self.aircrafts]
        speed_dict, df_dist, time_dict, cost_dict = generateParameters(self.aircraftNames, self.airportNames, self.seed)
        self.time_dict = time_dict
        self.cost_dict = cost_dict
        self.df_days = generateDayValidPeriodsPerDay(n_days, start_hour, end_hour)
        self.tv_i = int(start_hour.total_seconds() / 60)
        self.tv_f = int(end_hour.total_seconds() / 60)
        self.last_picket_airport = ''

    def createItinerary(self, ac: str, px: str, pe: str, pf: str, py: str, t_ini: int, t_free: int, max_time: int,
                        key=None, next_possible_segments=None):
        if next_possible_segments is None:
            next_possible_segments = []

        if key is None:
            key = f"{uuid4()}"
        txe = self.time_dict[ac][px][pe]
        tef = self.time_dict[ac][pe][pf]
        tfy = self.time_dict[ac][pf][py]
        total_time = txe + tef + tfy + t_free
        t_fin = t_ini + total_time if t_ini + total_time < max_time else max_time
        pre_price = self.cost_dict[ac][px][pe]
        trip_price = self.cost_dict[ac][pe][pf]
        post_price = self.cost_dict[ac][pf][py]
        pre_flight = Flight(fromAirport=px, toAirport=pe, price=pre_price, timeInMin=txe)
        trip_flight = Flight(fromAirport=pe, toAirport=pf, price=trip_price, timeInMin=tef)
        post_flight = Flight(fromAirport=pf, toAirport=py, price=post_price, timeInMin=tfy)
        return ProcessedItinerary(key=key, segmentStart=t_ini, segmentEnd=t_fin,
                                  preReposition=pre_flight, trip=trip_flight, posReposition=post_flight,
                                  nextPossibleSegments=next_possible_segments)

    def selectRandomAirport(self, ):
        if self.seed is not None:
            random.seed(self.seed)
        self.seed += random.randint(1, 50)
        return self.airportNames[random.randint(1, 50) % len(self.airportNames)]

    def generateTimeInitialAndPositions(self, t_disp_ini):
        if self.seed is not None:
            random.seed(self.seed)
        t_ini = t_disp_ini + randint(0, int((self.tv_f - self.tv_i) / 10))
        pos_ini = self.selectRandomAirport()
        pos_fin = self.selectRandomAirport()
        t_free = t_disp_ini + randint(0, int((self.tv_f - self.tv_i) / 5))
        return t_ini, pos_ini, pos_fin, t_free

    def generateAircraftCase(self, aircraft_case: ProcessedAircraftData, ac, from_airport, to_airport):
        if self.seed is not None:
            random.seed(self.seed)

        continuous_segments_ids = list()
        origen_continuous, destiny_continuous = self.selectRandomAirport(), self.selectRandomAirport()
        for d in self.df_days.index:
            key = uuid4()
            if randint(1, 1000) % 2 == 0 and len(continuous_segments_ids) == 0:
                # generate continuous segments
                continuous_segments_ids = [f"{key}"] + [f'{uuid4()}' for _ in range(1, 3)]
                origen_continuous, destiny_continuous = self.selectRandomAirport(), self.selectRandomAirport()

            if len(continuous_segments_ids) > 0:
                # generate continuous segments
                _key = continuous_segments_ids[0]

                t_ini, pos_ini, pos_fin, t_free = self.generateTimeInitialAndPositions(self.df_days['ini'].loc[d])
                departure_itinerary = self.createItinerary(ac=ac, px=origen_continuous,
                                                           pe=from_airport, pf=to_airport,
                                                           py=destiny_continuous, t_ini=t_ini, t_free=t_free,
                                                           max_time=self.df_days['end'].loc[d],
                                                           key=f"{_key}", next_possible_segments=continuous_segments_ids)

                return_itinerary = self.createItinerary(ac=ac, px=origen_continuous,
                                                        pe=to_airport, pf=from_airport,
                                                        py=destiny_continuous, t_ini=t_ini, t_free=t_free,
                                                        max_time=self.df_days['end'].loc[d],
                                                        key=f"{_key}", next_possible_segments=continuous_segments_ids)
                # for the next continuous segments
                continuous_segments_ids = continuous_segments_ids[1:]

                aircraft_case.departureItineraryArray.append(departure_itinerary)
                aircraft_case.returnItineraryArray.append(return_itinerary)

            else:
                # in different segments:
                t_ini, pos_ini, pos_fin, t_free = self.generateTimeInitialAndPositions(self.df_days['ini'].loc[d])
                departure_itinerary = self.createItinerary(ac=ac, px=pos_ini,
                                                           pe=from_airport, pf=to_airport, py=pos_fin,
                                                           t_ini=t_ini, t_free=t_free,
                                                           max_time=self.df_days['end'].loc[d],
                                                           key=f"{key}", next_possible_segments=[f"{key}"])
                return_itinerary = self.createItinerary(ac=ac, px=pos_ini,
                                                        pe=to_airport, pf=from_airport, py=pos_fin,
                                                        t_ini=t_ini, t_free=t_free,
                                                        max_time=self.df_days['end'].loc[d],
                                                        key=f"{key}", next_possible_segments=[f"{key}"])

                to_eval = randint(1, 1000)
                if to_eval % 2 == 0:
                    aircraft_case.departureItineraryArray.append(departure_itinerary)
                elif to_eval % 3 == 0:
                    aircraft_case.returnItineraryArray.append(return_itinerary)
                else:
                    aircraft_case.departureItineraryArray.append(departure_itinerary)
                    aircraft_case.returnItineraryArray.append(return_itinerary)

        return aircraft_case

    def generateStudyCaseRoundTrip(self, from_airport: str, to_airport: str):
        aircraft_study_case = list()
        aircraft_dict = dict()
        for ac in self.aircrafts:
            aircraft_dict[ac.aircraftCode] = ac

        for ac in self.aircraftNames:
            aircraft_case = ProcessedAircraftData(processedAircraft=aircraft_dict[ac],
                                                  departureItineraryArray=[], returnItineraryArray=[])
            aircraft_case = self.generateAircraftCase(aircraft_case, ac, from_airport, to_airport)
            aircraft_study_case.append(aircraft_case)

        return aircraft_study_case
