"""生成翻译文件中的动态字段映射"""
import json

# ============ 中文翻译 ============
zh = {
    "config": {
        "step": {
            "user": {
                "data": {
                    "class_name": "班级名称",
                    "student_name": "学生姓名",
                    "periods_per_day": "每天几节课",
                    "saturday_class": "周六有课",
                    "sunday_class": "周日有课"
                },
                "description": "添加课程表 - 填写基本信息后点击下一步",
                "title": "添加课程表"
            },
            "time_slots": {
                "data": {},
                "description": "设置每节课的上课和下课时间（格式 HH:MM，如 08:00）",
                "title": "上课时间设置"
            },
            "schedule": {
                "data": {},
                "description": "为每一天的每一节课填写科目（可自行输入任意科目名称，如：语文、数学、英语、道法、啦啦操、足球、诵读等）",
                "title": "课程安排"
            }
        },
        "error": {
            "time_order_error": "下课时间必须晚于上课时间，请检查后重新提交"
        },
        "abort": {
            "already_configured": "该课程表已配置"
        }
    },
    "options": {
        "step": {
            "init": {
                "data": {
                    "class_name": "班级名称",
                    "student_name": "学生姓名",
                    "periods_per_day": "每天几节课",
                    "saturday_class": "周六有课",
                    "sunday_class": "周日有课"
                },
                "description": "修改课程表基本信息（修改节数将重新设置时间表）",
                "title": "编辑课程表"
            }
        }
    },
    "entity": {
        "sensor": {
            "today_schedule": {"name": "今日课程"},
            "current_class": {"name": "当前课程"},
            "next_class": {"name": "下节课"},
            "class_countdown": {"name": "距离下课"}
        }
    }
}

# 动态字段：时间段 (1-15节)
for i in range(1, 16):
    zh["config"]["step"]["time_slots"]["data"][f"period_{i}_start"] = f"第{i}节 上课时间"
    zh["config"]["step"]["time_slots"]["data"][f"period_{i}_end"] = f"第{i}节 下课时间"

# 动态字段：课程安排 (7天 x 15节)
weekdays_cn = {"monday": "周一", "tuesday": "周二", "wednesday": "周三", "thursday": "周四", "friday": "周五", "saturday": "周六", "sunday": "周日"}
for day_key, day_cn in weekdays_cn.items():
    for i in range(1, 16):
        zh["config"]["step"]["schedule"]["data"][f"{day_key}_period_{i}"] = f"{day_cn} 第{i}节"

with open(r"Z:\custom_components\Classschedule\translations\zh-Hans.json", "w", encoding="utf-8") as f:
    json.dump(zh, f, ensure_ascii=False, indent=2)
print("zh-Hans.json done")

# ============ 英文翻译 ============
en = {
    "config": {
        "step": {
            "user": {
                "data": {
                    "class_name": "Class Name",
                    "student_name": "Student Name",
                    "periods_per_day": "Periods Per Day",
                    "saturday_class": "Saturday Class",
                    "sunday_class": "Sunday Class"
                },
                "description": "Add a class schedule - fill in basic info then click Next",
                "title": "Add Class Schedule"
            },
            "time_slots": {
                "data": {},
                "description": "Set start and end time for each period (format HH:MM, e.g. 08:00)",
                "title": "Time Slot Settings"
            },
            "schedule": {
                "data": {},
                "description": "Enter subject for each period on each day (free text input)",
                "title": "Schedule Arrangement"
            }
        },
        "error": {
            "time_order_error": "End time must be later than start time"
        },
        "abort": {
            "already_configured": "This schedule is already configured"
        }
    },
    "options": {
        "step": {
            "init": {
                "data": {
                    "class_name": "Class Name",
                    "student_name": "Student Name",
                    "periods_per_day": "Periods Per Day",
                    "saturday_class": "Saturday Class",
                    "sunday_class": "Sunday Class"
                },
                "description": "Modify basic info (changing period count will reset time slots)",
                "title": "Edit Class Schedule"
            }
        }
    },
    "entity": {
        "sensor": {
            "today_schedule": {"name": "Today's Schedule"},
            "current_class": {"name": "Current Class"},
            "next_class": {"name": "Next Class"},
            "class_countdown": {"name": "Time Until Class Ends"}
        }
    }
}

weekdays_en = {"monday": "Mon", "tuesday": "Tue", "wednesday": "Wed", "thursday": "Thu", "friday": "Fri", "saturday": "Sat", "sunday": "Sun"}
for i in range(1, 16):
    en["config"]["step"]["time_slots"]["data"][f"period_{i}_start"] = f"Period {i} Start"
    en["config"]["step"]["time_slots"]["data"][f"period_{i}_end"] = f"Period {i} End"

for day_key, day_en in weekdays_en.items():
    for i in range(1, 16):
        en["config"]["step"]["schedule"]["data"][f"{day_key}_period_{i}"] = f"{day_en} Period {i}"

with open(r"Z:\custom_components\Classschedule\translations\en.json", "w", encoding="utf-8") as f:
    json.dump(en, f, ensure_ascii=False, indent=2)
print("en.json done")

print("All translations generated!")
