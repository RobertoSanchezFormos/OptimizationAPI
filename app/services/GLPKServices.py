from typing import List

from modeling.classes.ProcessedAircraftData import ProcessedAircraftData
from modeling.models import minCostRoundTripModel


def run_round_trip_model_service(data: List[ProcessedAircraftData]):
    solver_results, model, summary = minCostRoundTripModel.run_model(data)
    if len(summary) > 0:
        return summary[0].to_dict()
