from typing import List

from app.core.exception_handler import INVALID_DATA_REQUEST_MSG
from modeling.classes.ProcessedAircraftData import ProcessedAircraftData
from modeling.models import minCostRoundTripModel
from modeling.models.minCostRoundTripAnswer import MinCostRoundTripAnswer


def run_round_trip_model_service(data: List[ProcessedAircraftData]):
    solver_results, model, summary = minCostRoundTripModel.run_model(data)
    if summary is not None and len(summary) > 0:
        return summary[0]
    non_valid_answer = MinCostRoundTripAnswer()
    non_valid_answer.msg = INVALID_DATA_REQUEST_MSG
    return non_valid_answer
