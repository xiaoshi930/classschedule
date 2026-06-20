"""课程表集成常量定义"""

DOMAIN = "classschedule"
PLATFORMS = ["sensor"]

# 配置键
CONF_CLASS_NAME = "class_name"
CONF_STUDENT_NAME = "student_name"
CONF_PERIODS_PER_DAY = "periods_per_day"
CONF_TIME_SLOTS = "time_slots"
CONF_SCHEDULE = "schedule"
CONF_ENTRIES = "entries"
CONF_SATURDAY_CLASS = "saturday_class"
CONF_SUNDAY_CLASS = "sunday_class"

# 默认值
DEFAULT_PERIODS_PER_DAY = 7
DEFAULT_SATURDAY_CLASS = False
DEFAULT_SUNDAY_CLASS = False

# 星期
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]
WEEKDAYS_CN = {
    "monday": "周一",
    "tuesday": "周二",
    "wednesday": "周三",
    "thursday": "周四",
    "friday": "周五",
    "saturday": "周六",
    "sunday": "周日",
}


def get_active_weekdays(config: dict) -> list:
    """根据配置返回活跃的星期列表（周一~周五 + 可选的周六/周日）"""
    days = list(WEEKDAYS)
    if config.get(CONF_SATURDAY_CLASS, DEFAULT_SATURDAY_CLASS):
        days.append("saturday")
    if config.get(CONF_SUNDAY_CLASS, DEFAULT_SUNDAY_CLASS):
        days.append("sunday")
    return days


