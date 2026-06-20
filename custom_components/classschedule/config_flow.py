"""课程表集成 - 配置流程"""

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_CLASS_NAME,
    CONF_STUDENT_NAME,
    CONF_PERIODS_PER_DAY,
    CONF_TIME_SLOTS,
    CONF_SCHEDULE,
    CONF_SATURDAY_CLASS,
    CONF_SUNDAY_CLASS,
    DEFAULT_PERIODS_PER_DAY,
    DEFAULT_SATURDAY_CLASS,
    DEFAULT_SUNDAY_CLASS,
    get_active_weekdays,
)

_LOGGER = logging.getLogger(__name__)

# 科目参考列表（用于显示建议，实际输入为自由文本）
SUBJECT_SUGGESTIONS = [
    # 主科
    "语文", "数学", "英语", "物理", "化学", "生物",
    "科学", "科学1", "科学2",
    # 文科
    "政治", "历史", "地理", "道法", "道德与法治",
    # 综合
    "物理/化学", "生物/地理", "历史/政治",
    # 艺术体育
    "音乐", "美术", "体育", "舞蹈", "啦啦操",
    # 活动
    "班会", "班队", "自习", "无课", "体游",
    # 特色课程
    "诵读", "写字", "书法", "足球", "篮球",
    "信息技术", "通用技术", "劳动", "综合实践",
    "心理", "心理健康", "校本课程", "阅读",
]


# 默认上课时间表
DEFAULT_TIMES = {
    1: ("08:20", "09:00"),
    2: ("09:15", "09:55"),
    3: ("10:25", "11:05"),
    4: ("11:20", "12:00"),
    5: ("14:20", "15:00"),
    6: ("15:15", "15:55"),
    7: ("16:20", "17:00"),
    8: ("17:15", "17:55"),
}


def _get_default_time(period: int, is_end: bool = False) -> str:
    """获取第 N 节课的默认时间"""
    if period in DEFAULT_TIMES:
        return DEFAULT_TIMES[period][1 if is_end else 0]
    # 超过8节的情况，按规律推算
    base_hour = 18 + (period - 9)
    base_min = 0
    return f"{base_hour:02d}:{base_min + (45 if is_end else 0):02d}"


def _build_time_slots_schema(periods: int, existing: dict = None) -> vol.Schema:
    """构建时间段配置 schema"""
    fields = {}
    for i in range(1, periods + 1):
        key_start = f"period_{i}_start"
        key_end = f"period_{i}_end"

        if existing:
            slots = existing.get(CONF_TIME_SLOTS, {})
            default_start = slots.get(key_start, _get_default_time(i, is_end=False))
            default_end = slots.get(key_end, _get_default_time(i, is_end=True))
        else:
            default_start = _get_default_time(i, is_end=False)
            default_end = _get_default_time(i, is_end=True)

        fields[vol.Required(key_start, default=default_start)] = str
        fields[vol.Required(key_end, default=default_end)] = str
    return vol.Schema(fields)


def _build_schedule_schema(periods: int, active_days: list, existing: dict = None) -> vol.Schema:
    """构建课程安排 schema（自由文本输入，支持任意科目名称）"""
    fields = {}
    for day in active_days:
        for i in range(1, periods + 1):
            key = f"{day}_period_{i}"
            default_val = ""
            if existing:
                sched = existing.get(CONF_SCHEDULE, {})
                default_val = sched.get(key, "")
            # 使用 cv.string 允许自由输入任意科目
            fields[vol.Required(key, default=default_val)] = cv.string
    return vol.Schema(fields)


class ClassScheduleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """课程表配置流程"""

    VERSION = 1

    def __init__(self):
        self._data = {}

    async def async_step_user(self, user_input=None):
        """第一步: 基本信息"""
        errors = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_time_slots()

        periods = self._data.get(CONF_PERIODS_PER_DAY, DEFAULT_PERIODS_PER_DAY)

        data_schema = vol.Schema({
            vol.Required(CONF_CLASS_NAME, default=""): str,
            vol.Required(CONF_STUDENT_NAME, default=""): str,
            vol.Required(CONF_PERIODS_PER_DAY, default=DEFAULT_PERIODS_PER_DAY): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=15)
            ),
            vol.Required(CONF_SATURDAY_CLASS, default=DEFAULT_SATURDAY_CLASS): bool,
            vol.Required(CONF_SUNDAY_CLASS, default=DEFAULT_SUNDAY_CLASS): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_time_slots(self, user_input=None):
        """第二步: 设置每节课时间段"""
        errors = {}
        periods = int(self._data.get(CONF_PERIODS_PER_DAY, DEFAULT_PERIODS_PER_DAY))

        if user_input is not None:
            # 验证时间格式和顺序
            time_data = {}
            for i in range(1, periods + 1):
                key_start = f"period_{i}_start"
                key_end = f"period_{i}_end"
                t_start = user_input.get(key_start, "")
                t_end = user_input.get(key_end, "")
                time_data[key_start] = t_start
                time_data[key_end] = t_end

                # 验证时间顺序
                if t_start and t_end:
                    if t_start >= t_end:
                        errors["base"] = "time_order_error"
                        break

            if not errors:
                self._data[CONF_TIME_SLOTS] = time_data
                return await self.async_step_schedule()

        schema = _build_time_slots_schema(periods, self._data if user_input is None else None)
        return self.async_show_form(
            step_id="time_slots",
            data_schema=schema,
            errors=errors,
            description_placeholders={"periods": str(periods)},
        )

    async def async_step_schedule(self, user_input=None):
        """第三步: 设置每天每节课的科目"""
        errors = {}
        periods = int(self._data.get(CONF_PERIODS_PER_DAY, DEFAULT_PERIODS_PER_DAY))
        active_days = get_active_weekdays(self._data)

        if user_input is not None:
            self._data[CONF_SCHEDULE] = dict(user_input)

            # 生成唯一 ID
            class_name = self._data.get(CONF_CLASS_NAME, "")
            student_name = self._data.get(CONF_STUDENT_NAME, "")
            title = f"{class_name} - {student_name}" if student_name else class_name

            return self.async_create_entry(
                title=title,
                data=self._data,
            )

        schema = _build_schedule_schema(periods, active_days, self._data)
        return self.async_show_form(
            step_id="schedule",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """支持选项修改"""
        return ClassScheduleOptionsFlowHandler(config_entry)


class ClassScheduleOptionsFlowHandler(config_entries.OptionsFlow):
    """选项修改流程"""

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self._data = dict(config_entry.data)

    async def async_step_init(self, user_input=None):
        """修改基本信息和课程"""
        errors = {}

        if user_input is not None:
            # 如果修改了节数，重新进入时间段和课程设置
            new_periods = int(user_input.get(CONF_PERIODS_PER_DAY, DEFAULT_PERIODS_PER_DAY))
            self._data.update(user_input)

            if new_periods != self.config_entry.data.get(CONF_PERIODS_PER_DAY, DEFAULT_PERIODS_PER_DAY):
                return await self.async_step_time_slots()

            return await self.async_step_time_slots()

        data_schema = vol.Schema({
            vol.Required(
                CONF_CLASS_NAME,
                default=self.config_entry.data.get(CONF_CLASS_NAME, ""),
            ): str,
            vol.Required(
                CONF_STUDENT_NAME,
                default=self.config_entry.data.get(CONF_STUDENT_NAME, ""),
            ): str,
            vol.Required(
                CONF_PERIODS_PER_DAY,
                default=self.config_entry.data.get(CONF_PERIODS_PER_DAY, DEFAULT_PERIODS_PER_DAY),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=15)),
            vol.Required(
                CONF_SATURDAY_CLASS,
                default=self.config_entry.data.get(CONF_SATURDAY_CLASS, DEFAULT_SATURDAY_CLASS),
            ): bool,
            vol.Required(
                CONF_SUNDAY_CLASS,
                default=self.config_entry.data.get(CONF_SUNDAY_CLASS, DEFAULT_SUNDAY_CLASS),
            ): bool,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_time_slots(self, user_input=None):
        """修改时间段"""
        errors = {}
        periods = int(self._data.get(CONF_PERIODS_PER_DAY, DEFAULT_PERIODS_PER_DAY))

        if user_input is not None:
            time_data = {}
            for i in range(1, periods + 1):
                key_start = f"period_{i}_start"
                key_end = f"period_{i}_end"
                time_data[key_start] = user_input.get(key_start, "")
                time_data[key_end] = user_input.get(key_end, "")

            self._data[CONF_TIME_SLOTS] = time_data
            return await self.async_step_schedule()

        existing = {}
        existing[CONF_TIME_SLOTS] = self.config_entry.data.get(CONF_TIME_SLOTS, {})
        schema = _build_time_slots_schema(periods, existing)
        return self.async_show_form(
            step_id="time_slots",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_schedule(self, user_input=None):
        """修改课程安排"""
        errors = {}
        periods = int(self._data.get(CONF_PERIODS_PER_DAY, DEFAULT_PERIODS_PER_DAY))
        active_days = get_active_weekdays(self._data)

        if user_input is not None:
            self._data[CONF_SCHEDULE] = dict(user_input)

            class_name = self._data.get(CONF_CLASS_NAME, "")
            student_name = self._data.get(CONF_STUDENT_NAME, "")
            title = f"{class_name} - {student_name}" if student_name else class_name

            self.hass.config_entries.async_update_entry(
                self.config_entry, data=self._data, title=title
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        existing = {}
        existing[CONF_SCHEDULE] = self.config_entry.data.get(CONF_SCHEDULE, {})
        schema = _build_schedule_schema(periods, active_days, existing)
        return self.async_show_form(
            step_id="schedule",
            data_schema=schema,
            errors=errors,
        )
