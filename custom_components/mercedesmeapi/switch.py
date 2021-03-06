"""
Support for Mercedes cars with Mercedes ME.

For more details about this component, please refer to the documentation at
https://github.com/ReneNulschDE/mbapipy/
"""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_OFF, STATE_ON

from custom_components.mercedesmeapi import DOMAIN, MercedesMeEntity
from .const import SWITCHES

DEPENDENCIES = ['mercedesmeapi']

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_devices,
                               discovery_info=None):
    """Setup the sensor platform."""
    if discovery_info is None:
        return

    data = hass.data[DOMAIN].data

    if not data.cars:
        _LOGGER.info("No Cars found.")
        return

    devices = []
    for car in data.cars:
        for key, value in sorted(SWITCHES.items()):
            if value[5] is None or getattr(car.features, value[5]) is True:
                devices.append(
                    MercedesMESwitch(
                        hass=hass,
                        data=data,
                        internal_name=key,
                        sensor_name=value[0],
                        vin=car.finorvin,
                        unit=value[1],
                        licenseplate=car.licenseplate,
                        feature_name=value[2],
                        object_name=value[3],
                        attrib_name=value[4],
                        extended_attributes=value[6],
                        switch_action=value[7]))

    async_add_devices(devices, True)


class MercedesMESwitch(MercedesMeEntity, SwitchEntity):
    """Representation of a Sensor."""

    @property
    def is_on(self):
        """Get whether the lock is in locked state."""
        return True if self.state == STATE_ON else False

    def turn_off(self, **kwargs):
        """Send the lock command."""
        _LOGGER.debug("turn off %s for: %s",
                      self._kwargs.get('switch_action', None), self._name)

        self._data.switch_car_feature(
            action='%s_off' % self._kwargs.get('switch_action', None),
            car_id=self._vin)

    def turn_on(self, **kwargs):
        """Send the unlock command."""
        _LOGGER.debug("turn on %s for: %s",
                      self._kwargs.get('switch_action', None), self._name)

        self._data.switch_car_feature(
            action='%s_on' % self._kwargs.get('switch_action', None),
            car_id=self._vin)

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._kwargs.get('switch_action', None) == 'climate':
            return STATE_OFF if self._state == 'INACTIVE' else STATE_ON

        if self._kwargs.get('switch_action', None) == 'heater':
            return STATE_OFF if not self._state else STATE_ON

        if self._kwargs.get('switch_action', None) == 'remote_start':
            return STATE_ON if self._state == 'RUNNING_FROM_REMOTESTART' \
                else STATE_OFF
