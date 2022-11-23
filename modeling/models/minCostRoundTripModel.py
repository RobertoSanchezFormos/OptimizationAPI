from typing import List, Union
import pyomo.environ as pm
from pyomo.core import ConcreteModel
from pyomo.opt import SolverResults

from modeling.classes.ProcessedAircraftData import ProcessedAircraftData
from modeling.classes.ProcessedItinerary import ProcessedItinerary
from modeling.models.utils import dataToDict

model_name = 'minCostRoundTripModel v1.0'


def calCostWithDetails(model: pm.ConcreteModel, ac1: str, ac2: str, it_i: int, it_j: int,
                       departure: ProcessedItinerary, back: ProcessedItinerary):
    if departure.key == back.key:
        # this implies two itineraries that belong to the same segment:
        # This simplifies: x->e, e->f, f->y | y->f, f->e, e->z
        # to:    x->e, e->f |  f->e, e->z
        return model.bs[ac1, ac2, it_i, it_j] * (departure.preTripPrice() + back.tripPosPrice())
    else:
        return model.bs[ac1, ac2, it_i, it_j] * (departure.preTripPosPrice() + back.preTripPosPrice())


def run_model(data: List[ProcessedAircraftData], n_best: int = 1) -> tuple[SolverResults, ConcreteModel]:
    """ PREPARE INFORMATION """
    data_dict = dataToDict(data)
    aircrafts = data_dict.keys()

    n_departure = max([len(d.departureItineraryArray) for d in data])
    n_return = max([len(d.returnItineraryArray) for d in data])

    indexes = [(a1, a2, i, j) for a1 in aircrafts for a2 in aircrafts for i in range(n_departure) for j in
               range(n_return) if i <= j]

    """ MODELING """
    # model declaration
    model = pm.ConcreteModel(model_name)

    # selection variables
    model.bs = pm.Var(indexes, domain=pm.Boolean, initialize=False)

    # objetive function
    def calCostTotal(ac1: str, ac2: str, it_i: int, it_j: int):
        if it_i >= len(data_dict[ac1].departureItineraryArray) or it_j >= len(data_dict[ac2].returnItineraryArray):
            # this prevents outside of index
            return 0
        return calCostWithDetails(model, ac1, ac2, it_i, it_j,
                                  departure=data_dict[ac1].departureItineraryArray[it_i],
                                  back=data_dict[ac1].returnItineraryArray[it_i])

    objective = sum(calCostTotal(a1, a2, i, j) for a1, a2, i, j in indexes)
    model.cost = pm.Objective(expr=objective, sense=pm.minimize)

    # Constraints:
    # How many best solutions constraint
    n_solutions = sum(model.bs[a1, a2, i, j] for a1, a2, i, j in indexes) == n_best
    model.n_solutions = pm.Constraint(expr=n_solutions)

    # Only valid combinations allowed
    def invalidCombination(m, ac1: str, ac2: str, it_i: int, it_j: int):
        if it_i >= len(data_dict[ac1].departureItineraryArray) or it_j >= len(data_dict[ac2].returnItineraryArray):
            # This combination does not exist thus this decision variable must be zero
            return m.bs[ac1, ac2, it_i, it_j] == 0
        return pm.Constraint.Skip

    model.invalidCombination = pm.Constraint(indexes, rule=invalidCombination)

    # Only feasible round trips
    def nonFeasibleRoundTrip(m, ac1: str, ac2: str, it_i: int, it_j: int):
        if it_i < len(data_dict[ac1].departureItineraryArray) and it_j < len(data_dict[ac2].returnItineraryArray):
            departure_itinerary = data_dict[ac1].departureItineraryArray[it_i]
            return_itinerary = data_dict[ac2].returnItineraryArray[it_j]

            if departure_itinerary.segmentEnd > return_itinerary.segmentStart:
                return m.bs[ac1, ac2, it_i, it_j] == 0
        return pm.Constraint.Skip

    model.nonFeasibleRoundTrip = pm.Constraint(indexes, rule=nonFeasibleRoundTrip)

    solver = pm.SolverFactory('glpk')
    results = solver.solve(model)
    return results, model
