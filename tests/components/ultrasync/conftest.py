"""Define fixtures available for all tests."""
from pytest import fixture

from tests.async_mock import MagicMock, patch

MOCK_AREAS_0 = [
    {"bank": 0, "name": "Area 1", "sequence": 30, "status": "Ready"},
]

MOCK_AREAS_1 = [
    {"bank": 0, "name": "Area 1", "sequence": 31, "status": "Not Ready"},
    # A dummy invalid bank to trigger throwing an invalid sensor update
    # for test coverage...
    {"bank": 98, "name": "Invalid", "sequence": 0, "status": "Ready"},
]

MOCK_ZONES_0 = [
    {"bank": 0, "name": "Front door", "sequence": 1, "status": "Ready"},
    {"bank": 1, "name": "Back door", "sequence": 1, "status": "Ready"},
]

MOCK_ZONES_1 = [
    {"bank": 0, "name": "Front door", "sequence": 2, "status": "Not Ready"},
    {"bank": 1, "name": "Back door", "sequence": 1, "status": "Ready"},
    # A dummy invalid bank to trigger throwing an invalid sensor update
    # for test coverage...
    {"bank": 98, "name": "Invalid", "sequence": 0, "status": "Ready"},
]

MOCK_RESPONSES = (
    {
        "areas": MOCK_AREAS_0,
        "zones": MOCK_ZONES_0,
    },
    {
        "areas": MOCK_AREAS_1,
        "zones": MOCK_ZONES_1,
    },
)


@fixture
def ultrasync_api(hass):
    """Mock UltraSync for easier testing."""

    with patch("ultrasync.UltraSync") as mock_api:
        instance = mock_api.return_value
        instance.login = MagicMock(return_value=True)
        instance.details = MagicMock(side_effect=MOCK_RESPONSES)
        instance.areas = MagicMock(return_value=list(MOCK_AREAS_0))
        instance.zones = MagicMock(return_value=list(MOCK_ZONES_0))
        yield mock_api
