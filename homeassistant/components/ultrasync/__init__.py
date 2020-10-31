"""The Interlogix UltraSync Hub component."""

import asyncio

from ultrasync import AlarmScene
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DATA_COORDINATOR,
    DATA_UNDO_UPDATE_LISTENER,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SERVICE_AWAY,
    SERVICE_DISARM,
    SERVICE_STAY,
)
from .coordinator import UltraSyncDataUpdateCoordinator

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistantType, config: dict) -> bool:
    """Set up the UltraSync integration."""
    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry) -> bool:
    """Set up UltraSync from a config entry."""
    if not entry.options:
        options = {
            CONF_SCAN_INTERVAL: entry.data.get(
                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
            ),
        }
        hass.config_entries.async_update_entry(entry, options=options)

    coordinator = UltraSyncDataUpdateCoordinator(
        hass,
        config=entry.data,
        options=entry.options,
    )

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    undo_listener = entry.add_update_listener(_async_update_listener)

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
        DATA_UNDO_UPDATE_LISTENER: undo_listener,
    }

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    _async_register_services(hass, coordinator)

    return True


async def async_unload_entry(hass: HomeAssistantType, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    if unload_ok:
        hass.data[DOMAIN][entry.entry_id][DATA_UNDO_UPDATE_LISTENER]()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


def _async_register_services(
    hass: HomeAssistantType,
    coordinator: UltraSyncDataUpdateCoordinator,
) -> None:
    """Register integration-level services."""

    def away(call) -> None:
        """Service call to set alarm system to 'away' mode in UltraSync Hub."""
        coordinator.hub.set(state=AlarmScene.AWAY)

    def stay(call) -> None:
        """Service call to set alarm system to 'stay' mode in UltraSync Hub."""
        coordinator.hub.set(state=AlarmScene.STAY)

    def disarm(call) -> None:
        """Service call to disable alarm in UltraSync Hub."""
        coordinator.hub.set(state=AlarmScene.DISARMED)

    hass.services.async_register(DOMAIN, SERVICE_AWAY, away, schema=vol.Schema({}))
    hass.services.async_register(DOMAIN, SERVICE_STAY, stay, schema=vol.Schema({}))
    hass.services.async_register(DOMAIN, SERVICE_DISARM, disarm, schema=vol.Schema({}))


async def _async_update_listener(hass: HomeAssistantType, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


class UltraSyncEntity(CoordinatorEntity):
    """Defines a base UltraSync entity."""

    def __init__(
        self, *, entry_id: str, name: str, coordinator: UltraSyncDataUpdateCoordinator
    ) -> None:
        """Initialize the UltraSync entity."""
        super().__init__(coordinator)
        self._name = name
        self._entry_id = entry_id

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name
