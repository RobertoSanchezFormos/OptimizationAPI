from typing import List, Union, Tuple
import pyomo.environ as pm
from pyomo.core import ConcreteModel
from pyomo.opt import SolverResults

from modeling.classes.ProcessedAircraftData import ProcessedAircraftData
from modeling.classes.ProcessedItinerary import ProcessedItinerary
from modeling.models.utils import dataToDict, is_valid_solution

model_name = 'minCostRoundTripModel v1.0'


def calCostWithDetails(departure: ProcessedItinerary, back: ProcessedItinerary):
    is_same_segment = False
    if departure.key == back.key:
        # this implies two itineraries that belong to the same segment:
        # This simplifies: x->e, e->f, f->y | y->f, f->e, e->z
        # to:    x->e, e->f |  f->e, e->z
        cost = departure.preTripPrice() + back.tripPosPrice()
        is_same_segment = True
    else:
        cost = departure.preTripPosPrice() + back.preTripPosPrice()

    return dict(cost=cost, isSameSegment=is_same_segment)


def run_model(data: List[ProcessedAircraftData], n_best: int = 1) -> Union[Tuple[None, None, None],
                                                                           Tuple[SolverResults, ConcreteModel, dict]]:
    """ PREPARE INFORMATION """
    data_dict = dataToDict(data)
    aircrafts = list(data_dict.keys())

    n_departure = max([len(d.departureItineraryArray) for d in data])
    n_return = max([len(d.returnItineraryArray) for d in data])

    if n_departure == 0 or n_return == 0:
        return None, None, None

    indexes = [(a1, a2, i, j) for a1 in aircrafts for a2 in aircrafts for i in range(n_departure) for j in
               range(n_return) if i <= j]

    """ TO SAVE INFORMATION """
    cost_data = dict()

    """ MODELING """
    # model declaration
    model = pm.ConcreteModel(model_name)

    # selection variables
    model.bs = pm.Var(indexes, domain=pm.Boolean, initialize=False)

    # variable to save results:
    model.cost = pm.Var(indexes, domain=pm.NonNegativeReals, initialize=0)

    # objetive function
    def calCostTotal(ac1: str, ac2: str, it_i: int, it_j: int):
        if it_i >= len(data_dict[ac1].departureItineraryArray) or it_j >= len(data_dict[ac2].returnItineraryArray):
            # this prevents outside of index
            return 0
        cost = calCostWithDetails(departure=data_dict[ac1].departureItineraryArray[it_i],
                                  back=data_dict[ac2].returnItineraryArray[it_j])
        cost_data[model.bs[ac1, ac2, it_i, it_j].name] = dict(ac1=ac1, ac2=ac2, it_i=it_i, it_j=it_j, cost=cost)
        return model.bs[ac1, ac2, it_i, it_j] * cost['cost']

    objective = sum(calCostTotal(a1, a2, i, j) for a1, a2, i, j in indexes)
    model.objective = pm.Objective(expr=objective, sense=pm.minimize)

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
    solver_results = solver.solve(model)
    summary = get_final_results(solver_results, model, cost_data, data_dict)

    return solver_results, model, summary


def get_final_results(solver_results, model, cost_data, data_dict):
    resp = list()
    if is_valid_solution(solver_results):
        for v in model.component_data_objects(pm.Var):
            if v.domain == pm.Boolean and v.value > 0:
                v_dict = cost_data[v.name]
                ac1, it_i, ac2, it_j = v_dict['ac1'], v_dict['it_i'], v_dict['ac2'], v_dict['it_j']
                departure = data_dict[ac1].departureItineraryArray[it_i]
                back = data_dict[ac2].departureItineraryArray[it_j]
                v_dict['departure'] = departure
                v_dict['back'] = back
                resp.append(cost_data[v.name])
    return resp
