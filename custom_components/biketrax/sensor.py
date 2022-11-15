"""Support for reading device status from BikeTrax."""
from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from aiobiketrax import Device
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    LENGTH_KILOMETERS,
    LENGTH_METERS,
    PERCENTAGE,
    SPEED_KILOMETERS_PER_HOUR,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import BikeTraxBaseEntity
from .const import DATA_DEVICE, DATA_SUBSCRIPTION, DOMAIN
from .coordinator import BikeTraxDataUpdateCoordinator


@dataclass
class BikeTraxRequiredKeysMixin:
    """Mixin for required keys."""

    coordinator: str


@dataclass
class BikeTraxSensorEntityDescription(
    SensorEntityDescription, BikeTraxRequiredKeysMixin
):
    """Describes BikeTrax sensor entity."""


SENSOR_TYPES: tuple[BikeTraxSensorEntityDescription, ...] = (
    BikeTraxSensorEntityDescription(
        coordinator=DATA_DEVICE,
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        key="battery_level",
        name="Battery level",
        native_unit_of_measurement=PERCENTAGE,
    ),
    BikeTraxSensorEntityDescription(
        coordinator=DATA_DEVICE,
        device_class=SensorDeviceClass.DISTANCE,
        icon="mdi:speedometer",
        key="total_distance",
        name="Total distance",
        native_unit_of_measurement=LENGTH_KILOMETERS,
    ),
    BikeTraxSensorEntityDescription(
        coordinator=DATA_DEVICE,
        device_class=SensorDeviceClass.SPEED,
        icon="mdi:speedometer",
        key="speed",
        name="Current speed",
        native_unit_of_measurement=SPEED_KILOMETERS_PER_HOUR,
    ),
    BikeTraxSensorEntityDescription(
        coordinator=DATA_SUBSCRIPTION,
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:license",
        key="subscription_until",
        name="Subscription until",
    ),
    BikeTraxSensorEntityDescription(
        coordinator=DATA_DEVICE,
        icon="mdi:state-machine",
        key="status",
        name="Device status",
    ),
    BikeTraxSensorEntityDescription(
        coordinator=DATA_DEVICE,
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock",
        key="last_updated",
        name="Last updated",
    ),
    BikeTraxSensorEntityDescription(
        coordinator=DATA_DEVICE,
        icon="mdi:border-radius",
        key="guard_type",
        name="Auto alarm type",
    ),
    BikeTraxSensorEntityDescription(
        coordinator=DATA_DEVICE,
        device_class=SensorDeviceClass.DISTANCE,
        icon="mdi:map-marker-distance",
        key="geofence_radius",
        name="Auto alarm geofence radius",
        native_unit_of_measurement=LENGTH_METERS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BikeTrax sensors from config entry."""

    coordinators: dict[str, BikeTraxDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        BikeTraxSensor(coordinators[description.coordinator], device, description)
        for description in SENSOR_TYPES
        for device in coordinators[description.coordinator].account.devices
    ]

    async_add_entities(entities)


class BikeTraxSensor(BikeTraxBaseEntity, SensorEntity):
    """Representation of a BikeTrax device sensor."""

    entity_description: BikeTraxSensorEntityDescription

    def __init__(
        self,
        coordinator: BikeTraxDataUpdateCoordinator,
        device: Device,
        description: BikeTraxSensorEntityDescription,
    ) -> None:
        """Initialize BikeTrax device sensor."""
        super().__init__(coordinator, device)

        self.entity_description = description
        self.entity_id = f"{SENSOR_DOMAIN}.{DOMAIN}_{description.key}_{device.id}"

        self._attr_device_class = description.device_class
        self._attr_entity_category = description.entity_category
        self._attr_name = f"{device.name} {description.name}"
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_unique_id = f"{device.id}-{description.key}"

    @property
    def native_value(self) -> StateType:
        return cast(StateType, getattr(self.device, self.entity_description.key))
