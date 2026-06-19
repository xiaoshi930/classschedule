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

# 默认值
DEFAULT_PERIODS_PER_DAY = 7

# 星期
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]
WEEKDAYS_CN = {
    "monday": "周一",
    "tuesday": "周二",
    "wednesday": "周三",
    "thursday": "周四",
    "friday": "周五",
}


