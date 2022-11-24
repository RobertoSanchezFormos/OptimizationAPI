from fastapi import APIRouter
from app.schemas import GLPKSchema
from app.services.GLPKServices import run_round_trip_model_service
from modeling.classes.ProcessedAircraftData import ProcessedAircraftData

router = APIRouter(
    prefix="/opt",
    tags=["opt"],
    responses={404: {"description": "Not found"}},
)


@router.post('/round-trip', response_model=GLPKSchema.MinCostRoundTripAnswerSC)
def solve_round_trip_optimization_problem(data: GLPKSchema.CalendarInformationSC):
    valid_processed_aircraft_data = [ProcessedAircraftData(**p.dict()) for p in data.processedAircraftData]
    response = run_round_trip_model_service(valid_processed_aircraft_data)
    return response.to_dict()

