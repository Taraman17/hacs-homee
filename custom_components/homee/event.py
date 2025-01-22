"""The homee event platform."""

from pyHomee.const import AttributeType
from pyHomee.model import HomeeAttribute

from homeassistant.components.event import (
    EventDeviceClass,
    EventEntity,
    EventEntityDescription,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback

from . import HomeeConfigEntry
from .entity import HomeeEntity
from .helpers import migrate_old_unique_ids


async def async_setup_entry(
    hass: HomeAssistant, config_entry: HomeeConfigEntry, async_add_devices
) -> None:
    """Add the homee platform for the event component."""

    devices = []
    for node in config_entry.runtime_data.nodes:
        devices.extend(
            HomeeEvent(attribute, config_entry)
            for attribute in node.attributes
            if (attribute.type == AttributeType.UP_DOWN_REMOTE)
        )
    if devices:
        await migrate_old_unique_ids(hass, devices, Platform.EVENT)
        async_add_devices(devices)


class HomeeEvent(HomeeEntity, EventEntity):
    """Representation of a homee event."""

    entity_description = EventEntityDescription(
        key="up_down_remote",
        device_class=EventDeviceClass.BUTTON,
        event_types=["0", "1", "2", "3", "4", "5", "6", "7", "9"],
        translation_key="up_down_remote",
        has_entity_name=True,
    )

    @property
    def old_unique_id(self) -> str:
        """Return the old not so unique id of the climate entity."""
        return f"{self._attribute.node_id}-event-{self._attribute.id}"

    @callback
    def _async_handle_event(self, event: HomeeAttribute) -> None:
        """Handle a homee event."""
        if event.type == AttributeType.UP_DOWN_REMOTE:
            self._trigger_event(str(int(event.current_value)))
            self.async_write_ha_state()
