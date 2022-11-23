import random
import datetime as dt

from modeling.classes.ItineraryGenerator import ItineraryGenerator
from modeling.models import minCostRoundTripModel
from modeling.models.utils import generateAircraftsAndAirports, generateParameters, print_results

n_aircrafts = 3
n_airports = 5


def test():
    aircrafts, airport_names = generateAircraftsAndAirports(n_aircrafts, n_airports)
    start_hour = dt.timedelta(hours=6)  # from 6 am
    end_hour = dt.timedelta(hours=20)  # to 20 pm
    itinerary_gen = ItineraryGenerator(aircrafts=aircrafts, airport_names=airport_names, n_days=5,
                                       start_hour=start_hour, end_hour=end_hour, seed=77)
    from_airport = 'airport1' if airport_names else airport_names[0]
    to_airport = 'airport3' if airport_names else airport_names[-1]

    study_case = itinerary_gen.generateStudyCaseRoundTrip(from_airport=from_airport, to_airport=to_airport)
    solver_results, model = minCostRoundTripModel.run_model(study_case)

    print_results(solver_results, model, print_model=False)


if __name__ == "__main__":
    test()
