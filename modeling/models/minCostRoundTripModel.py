from typing import List, Union, Tuple
import pyomo.environ as pm
from pyomo.core import ConcreteModel
from pyomo.opt import SolverResults

from modeling.classes.ProcessedAircraftData import ProcessedAircraftData
from modeling.classes.ProcessedItinerary import ProcessedItinerary
from modeling.models.minCostRoundTripAnswer import MinCostRoundTripAnswer
from modeling.models.utils import dataToDict, is_valid_solution, NON_SUCCESSFUL_SOLVER_SOLUTION_MSG, \
    SUCCESSFUL_SOLVER_SOLUTION_MSG

model_name = 'minCostRoundTripModel v1.0'


def calCostWithDetails(departure_itinerary: ProcessedItinerary, return_itinerary: ProcessedItinerary):
    is_same_segment_or_continuous = departure_itinerary.key == return_itinerary.key or \
                                return_itinerary.isNextPossibleSegmentOf(departure_itinerary)
    if is_same_segment_or_continuous:
        # this implies either these two itineraries belong to the same segment or they are continuous
        # therefore the following simplification applies.
        # This simplifies: x->e, e->f, f->y | y->f, f->e, e->z
        # with this:    x->e, e->f |  f->e, e->z
        cost = departure_itinerary.preTripPrice() + return_itinerary.tripPosPrice()
    else:
        cost = departure_itinerary.preTripPosPrice() + return_itinerary.preTripPosPrice()

    return dict(cost=cost, isSameSegmentOrContinuous=is_same_segment_or_continuous)


def run_model(data: List[ProcessedAircraftData], n_best: int = 1) -> Union[Tuple[None, None, None],
                                                                           Tuple[SolverResults, ConcreteModel, list]]:
    """ PREPARE INFORMATION """
    data_dict = dataToDict(data)
    aircrafts = list(data_dict.keys())

    n_departure = max([len(d.departureItineraryArray) for d in data])
    n_return = max([len(d.returnItineraryArray) for d in data])

    if n_departure == 0 or n_return == 0:
        return None, None, None

    indexes = [(a1, a2, i, j) for a1 in aircrafts for a2 in aircrafts for i in range(n_departure) for j in
               range(n_return) if i < len(data_dict[a1].departureItineraryArray)
               and j < len(data_dict[a2].returnItineraryArray)]

    """ TO SAVE INFORMATION """
    cost_data = dict()

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
        if ac1 == 'aircraft0' and ac2 == 'aircraft2' and it_i == 3 and it_j == 0:
            print('stop')
        resp = calCostWithDetails(departure_itinerary=data_dict[ac1].departureItineraryArray[it_i],
                                  return_itinerary=data_dict[ac2].returnItineraryArray[it_j])
        cost_data[model.bs[ac1, ac2, it_i, it_j].name] = dict(ac1=ac1, ac2=ac2, it_i=it_i, it_j=it_j, resp=resp)
        return model.bs[ac1, ac2, it_i, it_j] * resp['cost']

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
            # only for valid indexes:
            departure_itinerary: ProcessedItinerary = data_dict[ac1].departureItineraryArray[it_i]
            return_itinerary: ProcessedItinerary = data_dict[ac2].returnItineraryArray[it_j]

            if departure_itinerary.key == return_itinerary.key:
                # they belong to the same segment: pre + trip + pos should be inside the segment
                if departure_itinerary.preTripTimeInMin() + return_itinerary.tripPosTimeInMin() < return_itinerary.segmentTimeInMin:
                    # this schedule does not fit
                    return m.bs[ac1, ac2, it_i, it_j] == 0
            elif departure_itinerary.segmentEnd > return_itinerary.segmentStart:
                # different segments and schedule does not fit since return starts before the departure
                return m.bs[ac1, ac2, it_i, it_j] == 0
        # any other case is omitted
        return pm.Constraint.Skip

    model.nonFeasibleRoundTrip = pm.Constraint(indexes, rule=nonFeasibleRoundTrip)

    # The next trip should have greater or equal number of seats:
    def nonSeats(m, ac1: str, ac2: str, it_i: int, it_j: int):
        if it_i < len(data_dict[ac1].departureItineraryArray) and it_j < len(data_dict[ac2].returnItineraryArray):
            # only for valid indexes:
            departure_seats = data_dict[ac1].processedAircraft.seats
            return_seats = data_dict[ac2].processedAircraft.seats
            if return_seats - departure_seats < 0:
                # there is no room for other passenger
                return m.bs[ac1, ac2, it_i, it_j] == 0
        # any other case is omitted
        return pm.Constraint.Skip

    model.nonSeats = pm.Constraint(indexes, rule=nonSeats)

    solver = pm.SolverFactory('glpk')
    solver_results = solver.solve(model)
    summary = get_final_results(solver_results, model, cost_data, data_dict)

    return solver_results, model, summary


def get_final_results(solver_results, model, cost_data, data_dict) -> List[MinCostRoundTripAnswer]:
    resp = list()
    success = is_valid_solution(solver_results)
    if not success:
        answer = MinCostRoundTripAnswer()
        answer.isSuccess = success
        answer.msg = NON_SUCCESSFUL_SOLVER_SOLUTION_MSG
        return [answer]

    if success:
        for v in model.component_data_objects(pm.Var):
            if v.domain == pm.Boolean and v.value > 0:
                v_dict = cost_data[v.name]
                ac1, it_i, ac2, it_j = v_dict['ac1'], v_dict['it_i'], v_dict['ac2'], v_dict['it_j']
                answer = MinCostRoundTripAnswer()
                answer.isSuccess = success
                answer.msg = SUCCESSFUL_SOLVER_SOLUTION_MSG
                answer.departurePath = data_dict[ac1].departureItineraryArray[it_i]
                answer.returnPath = data_dict[ac2].returnItineraryArray[it_j]
                answer.departureAircraft = ac1
                answer.returnAircraft = ac2
                answer.price = v_dict['resp']['cost']
                answer.isSameSegmentOrContinuous = v_dict['resp']['isSameSegmentOrContinuous']
                resp.append(answer)
    return resp
