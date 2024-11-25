import pytest
from iiconstructor_core.domain.primitives import (
    Description,
    Name,
    ScenarioID,
    SourceInfo,
)
from iiconstructor_inmemory.repo import SourceInMemory


@pytest.fixture()
def get_source() -> SourceInMemory:
    scenario_id = ScenarioID(1)
Í
    name = Name("123")
    description = Description("qwe")

    source_info = SourceInfo(name, description)

    return SourceInMemory(scenario_id, source_info)
