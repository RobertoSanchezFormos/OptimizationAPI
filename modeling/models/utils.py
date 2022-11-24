import random
from random import uniform, randint
from typing import List
import pandas as pd
import datetime as dt

import pyomo.environ as pm

from modeling.classes.Aircraft import Aircraft
from modeling.classes.ProcessedAircraftData import ProcessedAircraftData


def dataToDict(data: List[ProcessedAircraftData]) -> dict:
    resp = dict()
    for p in data:
        resp[p.processedAircraft.aircraftCode] = p
    return resp


def generateAircraftsAndAirports(n_aircrafts, n_airports, seed=None):
    aircrafts = []
    if seed is not None:
        random.seed(seed)

    for i in range(n_aircrafts):
        code = f'aircraft{i}'
        aircraft = Aircraft(aircraftCode=code, seats=randint(3, 10))
        aircrafts.append(aircraft)

    airports = [f'airport{i}' for i in range(n_airports)]
    return aircrafts, airports


def generateSpeedKmH(aircrafts, seed=None):
    if seed is not None:
        random.seed(seed)
    speed = {}
    # km/h
    for ac in aircrafts:
        speed[ac] = 400 + 400 * uniform(0, 1)
    return speed


def generateDistanceMatrixKm(airports, seed=None):
    if seed is not None:
        random.seed(seed)
    # distance matrix: km
    df_dist = pd.DataFrame(index=airports, columns=airports)
    for ap_i in airports:
        for ap_j in airports:
            dist = 0 if ap_i == ap_j else randint(400, 1500)
            df_dist[ap_i].loc[ap_j] = dist
            df_dist[ap_j].loc[ap_i] = dist
    return df_dist


def generateTimeTripInMinutes(speed: dict, df_dist: pd.DataFrame, airports: list):
    aircrafts = speed.keys()
    time = {}
    for ac in aircrafts:
        df_time = pd.DataFrame(index=airports, columns=airports)
        for a_i in airports:
            for a_j in airports:
                t = round(df_dist[a_i][a_j] / (speed[ac] * (1 / 60)), 2)
                df_time[a_i][a_j] = t
                df_time[a_j][a_i] = t
            time[ac] = df_time
    return time


def generateCostTrip(aircrafts: list, airports: list, seed=None):
    if seed is not None:
        random.seed(seed)
    cost = {}
    for ac in aircrafts:
        df_cost = pd.DataFrame(index=airports, columns=airports)
        for a_i in airports:
            for a_j in airports:
                c = 0 if a_i == a_j else round(50 + 50 * uniform(0, 1), 2)
                df_cost[a_i].loc[a_j] = c
                df_cost[a_j].loc[a_i] = c

        cost[ac] = df_cost
    return cost


def generateParameters(aircrafts, airports, seed=None):
    if seed is not None:
        random.seed(seed)
    speed_dict = generateSpeedKmH(aircrafts, seed)
    df_dist = generateDistanceMatrixKm(airports, seed)
    time_dict = generateTimeTripInMinutes(speed_dict, df_dist, airports)
    cost_dict = generateCostTrip(aircrafts, airports, seed)
    return speed_dict, df_dist, time_dict, cost_dict


def generateDayValidPeriodsPerDay(n_days,
                                  initial_time: dt.timedelta = dt.timedelta(hours=6),
                                  final_time: dt.timedelta = dt.timedelta(hours=20)):
    one_day = dt.timedelta(days=1)

    t_i = initial_time  # time to start flights
    t_f = final_time  # time to finish flights
    days = [f'd{i}' for i in range(1, n_days + 1)]
    t_per_day = dt.timedelta(seconds=0, days=0, minutes=0)

    df_days = pd.DataFrame(index=days, columns=['ini', 'end'])
    for day in days:
        df_days['ini'].loc[day] = (t_per_day + t_i).total_seconds() / 60
        df_days['end'].loc[day] = (t_per_day + t_f).total_seconds() / 60
        t_per_day += one_day
    return df_days


def is_valid_solution(solver_results):
    return solver_results['Solver'][0]['Termination condition'] == 'optimal'


def print_results(solver_results, model, print_model: bool = False):
    print(solver_results['Solver'][0])
    if is_valid_solution(solver_results):
        if print_model:
            model.display()
        n_boolean = 0
        print('# ==========================================================\nSelected solution:')
        print('Variables:')
        for v in model.component_data_objects(pm.Var):
            if v.domain == pm.Boolean:
                if v.value < 1 or print(str(v), v.value):
                    n_boolean += 1

        print(f'\nA total of {n_boolean} boolean variables are False')

    else:
        for c in model.component_objects(ctype=pm.Constraint):
            print(c.display())
