from typing import Any, Dict

from dependencies import get_country_service, get_state_service
from fastapi import APIRouter, Depends
from schemas.catalog import CountryListResponseSchema, StateListResponseSchema
from services.country_service import CountryService
from services.state_service import StateService

router = APIRouter(prefix="/api/v1/paises", tags=["Paises"])


@router.get("/", response_model=CountryListResponseSchema)
def get_countries(service: CountryService = Depends(get_country_service)) -> Dict[str, Any]:
    return service.get_all_countries()


@router.get("/{pais_id}/estados", response_model=StateListResponseSchema)
def get_states_by_country(
    pais_id: str,
    service: StateService = Depends(get_state_service),
) -> Dict[str, Any]:
    return service.get_states_by_country_id(pais_id)


