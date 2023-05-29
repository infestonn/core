"""Support for the Airzone Cloud sensors."""
from __future__ import annotations

from typing import Any, Final

from aioairzone_cloud.const import (
    AZD_AIDOOS,
    AZD_HUMIDITY,
    AZD_NAME,
    AZD_TEMP,
    AZD_ZONES,
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AirzoneUpdateCoordinator
from .entity import AirzoneAidooEntity, AirzoneEntity, AirzoneZoneEntity

AIDOO_SENSOR_TYPES: Final[tuple[SensorEntityDescription, ...]] = (
    SensorEntityDescription(
        device_class=SensorDeviceClass.TEMPERATURE,
        key=AZD_TEMP,
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

ZONE_SENSOR_TYPES: Final[tuple[SensorEntityDescription, ...]] = (
    SensorEntityDescription(
        device_class=SensorDeviceClass.TEMPERATURE,
        key=AZD_TEMP,
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        device_class=SensorDeviceClass.HUMIDITY,
        key=AZD_HUMIDITY,
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add Airzone Cloud sensors from a config_entry."""
    coordinator: AirzoneUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors: list[AirzoneSensor] = []

    # Aidoos
    for aidoo_id, aidoo_data in coordinator.data.get(AZD_AIDOOS, {}).items():
        for description in AIDOO_SENSOR_TYPES:
            if description.key in aidoo_data:
                sensors.append(
                    AirzoneAidooSensor(
                        coordinator,
                        description,
                        entry,
                        aidoo_id,
                        aidoo_data,
                    )
                )

    # Zones
    for zone_id, zone_data in coordinator.data.get(AZD_ZONES, {}).items():
        for description in ZONE_SENSOR_TYPES:
            if description.key in zone_data:
                sensors.append(
                    AirzoneZoneSensor(
                        coordinator,
                        description,
                        entry,
                        zone_id,
                        zone_data,
                    )
                )

    async_add_entities(sensors)


class AirzoneSensor(AirzoneEntity, SensorEntity):
    """Define an Airzone Cloud sensor."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update attributes when the coordinator updates."""
        self._async_update_attrs()
        super()._handle_coordinator_update()

    @callback
    def _async_update_attrs(self) -> None:
        """Update sensor attributes."""
        self._attr_native_value = self.get_airzone_value(self.entity_description.key)


class AirzoneAidooSensor(AirzoneAidooEntity, AirzoneSensor):
    """Define an Airzone Cloud Aidoo sensor."""

    def __init__(
        self,
        coordinator: AirzoneUpdateCoordinator,
        description: SensorEntityDescription,
        entry: ConfigEntry,
        aidoo_id: str,
        aidoo_data: dict[str, Any],
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, entry, aidoo_id, aidoo_data)

        self._attr_name = f"{aidoo_data[AZD_NAME]} {description.name}"
        self._attr_unique_id = f"{entry.unique_id}_{aidoo_id}_{description.key}"
        self.entity_description = description

        self._async_update_attrs()


class AirzoneZoneSensor(AirzoneZoneEntity, AirzoneSensor):
    """Define an Airzone Cloud Zone sensor."""

    def __init__(
        self,
        coordinator: AirzoneUpdateCoordinator,
        description: SensorEntityDescription,
        entry: ConfigEntry,
        zone_id: str,
        zone_data: dict[str, Any],
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, entry, zone_id, zone_data)

        self._attr_name = f"{zone_data[AZD_NAME]} {description.name}"
        self._attr_unique_id = f"{entry.unique_id}_{zone_id}_{description.key}"
        self.entity_description = description

        self._async_update_attrs()
