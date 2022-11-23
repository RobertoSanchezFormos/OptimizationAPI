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

    def createItinerary(self, ac: str, px: str, pe: str, pf: str, py: str, t_ini: int, key=None):
        if key is None:
            key = f"{uuid4()}"
        txe = self.time_dict[ac][px][pe]
        tef = self.time_dict[ac][pe][pf]
        tfy = self.time_dict[ac][pf][py]
        total_time = txe + tef + tfy
        pre_price = self.cost_dict[ac][px][pe]
        trip_price = self.cost_dict[ac][pe][pf]
        post_price = self.cost_dict[ac][pf][py]
        pre_flight = Flight(fromAirport=px, toAirport=pe, price=pre_price, start_time=t_ini, end_time=t_ini + txe)
        trip_flight = Flight(fromAirport=pe, toAirport=pf, price=trip_price, start_time=t_ini + txe,
                             end_time=t_ini + txe + tef)
        post_flight = Flight(fromAirport=pf, toAirport=py, price=post_price, start_time=t_ini + txe + tef,
                             end_time=t_ini + total_time)
        return ProcessedItinerary(key=key, segmentStart=t_ini, segmentEnd=t_ini + total_time,
                                  preReposition=pre_flight, trip=trip_flight, posReposition=post_flight)

    def selectRandomAirport(self, ):
        if self.seed is not None:
            random.seed(self.seed)
        return self.airportNames[random.randint(1, 50) % len(self.airportNames)]

    def generateTimeInitialAndPositions(self, t_disp_ini):
        if self.seed is not None:
            random.seed(self.seed)
        t_ini = t_disp_ini + randint(0, int((self.tv_f - self.tv_i) / 10))
        pos_ini = self.selectRandomAirport()
        pos_fin = self.selectRandomAirport()
        return t_ini, pos_ini, pos_fin

    def generateAircraftCase(self, aircraft_case: ProcessedAircraftData, ac, from_airport, to_airport):
        if self.seed is not None:
            random.seed(self.seed)

        for d in self.df_days.index:
            key = uuid4()
            if randint(1, 1000) % 2 == 0:
                # in the same segment
                t_ini, pos_ini, pos_fin = self.generateTimeInitialAndPositions(self.df_days['ini'].loc[d])
                departure_itinerary = self.createItinerary(ac=ac, px=pos_ini,
                                                           pe=from_airport, pf=to_airport, py=pos_fin, t_ini=t_ini,
                                                           key=f"{key}")

                t_ini, pos_ini, pos_fin = self.generateTimeInitialAndPositions(departure_itinerary.segmentEnd)
                return_itinerary = self.createItinerary(ac=ac, px=pos_ini,
                                                        pe=from_airport, pf=to_airport, py=pos_fin, t_ini=t_ini,
                                                        key=f"{key}")
                aircraft_case.departureItineraryArray.append(departure_itinerary)
                aircraft_case.returnItineraryArray.append(return_itinerary)

            else:
                # in different segments:
                if randint(1, 1000) % 2 == 0:
                    t_ini, pos_ini, pos_fin = self.generateTimeInitialAndPositions(self.df_days['ini'].loc[d])
                    departure_itinerary = self.createItinerary(ac=ac, px=pos_ini,
                                                               pe=from_airport, pf=to_airport, py=pos_fin,
                                                               t_ini=t_ini,
                                                               key=f"{key}")
                    aircraft_case.departureItineraryArray.append(departure_itinerary)
                else:
                    t_ini, pos_ini, pos_fin = self.generateTimeInitialAndPositions(self.df_days['ini'].loc[d])
                    return_itinerary = self.createItinerary(ac=ac, px=pos_ini,
                                                            pe=from_airport, pf=to_airport, py=pos_fin,
                                                            t_ini=t_ini,
                                                            key=f"{key}")
                    aircraft_case.returnItineraryArray.append(return_itinerary)

        return aircraft_case

    def generateStudyCaseRoundTrip(self, from_airport: str, to_airport: str):
        aircraft_study_case = list()
        aircraft_dict = dict()
        for ac in self.aircrafts:
            aircraft_dict[ac.aircraftCode] = ac

        for ac in self.aircraftNames:
            aircraft_case = ProcessedAircraftData(processedAircraft=aircraft_dict[ac])
            aircraft_case = self.generateAircraftCase(aircraft_case, ac, from_airport, to_airport)
            aircraft_study_case.append(aircraft_case)

        return aircraft_study_case
