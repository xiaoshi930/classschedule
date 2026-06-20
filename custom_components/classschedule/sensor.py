"""课程表集成 - 传感器实体"""

import hashlib
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_CLASS_NAME,
    CONF_STUDENT_NAME,
    CONF_PERIODS_PER_DAY,
    CONF_TIME_SLOTS,
    CONF_SCHEDULE,
    WEEKDAYS_CN,
    get_active_weekdays,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置传感器实体"""
    async_add_entities([ClassScheduleSensor(entry.entry_id, dict(entry.data))], True)


class ClassScheduleSensor(SensorEntity):
    """课程表传感器"""

    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar-text"

    def __init__(self, entry_id: str, config_data: dict):
        self._entry_id = entry_id
        self._config = config_data

        class_name = config_data.get(CONF_CLASS_NAME, "")
        student_name = config_data.get(CONF_STUDENT_NAME, "")

        self._attr_unique_id = f"{entry_id}_schedule"
        self._attr_name = f"{student_name}课程表" if student_name else f"{class_name}课程表"

        # 生成 entity_id: sensor.class_schedule_xxx
        raw = student_name or class_name
        safe = re.sub(r"[^a-zA-Z0-9]", "", raw)
        if safe:
            self.entity_id = f"sensor.class_schedule_{safe.lower()}"
        else:
            h = hashlib.md5(raw.encode("utf-8")).hexdigest()[:6]
            self.entity_id = f"sensor.class_schedule_{h}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "课程表" + (f" - {class_name}" if class_name else ""),
            "manufacturer": "ClassSchedule",
            "model": "课程表",
        }

        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    def update(self) -> None:
        """更新传感器状态（仅构建静态课表属性）"""
        periods = int(self._config.get(CONF_PERIODS_PER_DAY, 7))
        time_slots = self._config.get(CONF_TIME_SLOTS, {})
        schedule = self._config.get(CONF_SCHEDULE, {})
        class_name = self._config.get(CONF_CLASS_NAME, "")
        student_name = self._config.get(CONF_STUDENT_NAME, "")

        full_schedule = {}
        active_days = get_active_weekdays(self._config)
        for day in active_days:
            day_cn = WEEKDAYS_CN[day]
            day_classes = {}
            for i in range(1, periods + 1):
                subject = schedule.get(f"{day}_period_{i}", "")
                day_classes[str(i)] = {
                    "科目": subject,
                    "开始": time_slots.get(f"period_{i}_start", ""),
                    "结束": time_slots.get(f"period_{i}_end", ""),
                }
            full_schedule[day_cn] = day_classes

        self._attr_native_value = class_name
        self._attr_extra_state_attributes = {
            "年级": class_name,
            "学生": student_name,
            "每天节数": periods,
            "课表详情": full_schedule,
        }
