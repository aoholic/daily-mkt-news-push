#!/usr/bin/env python3
"""判断某日是否为中国大陆法定工作日，供「每日营销简报」定时任务决定是否触发。

用法:
    python check_workday.py            # 判断今天
    python check_workday.py 2026-10-22 # 判断指定日期

输出 JSON:
    {
      "date": "2026-10-22",
      "weekday": "周四",
      "is_weekend": false,
      "in_holiday_table": false,   # 命中法定节假日表
      "in_workday_override": false,# 命中调休上班表
      "action": "触发" | "跳过" | "触发(未配置节假日数据)",
      "note": "..."
    }

维护说明:
    国务院办公厅每年 10-11 月发布次年放假安排。请把次年数据填入下面的
    HOLIDAYS / WORKDAY_OVERRIDES 两个表，否则本脚本退化为"周一至周五触发"的
    启发式判断，遇到调休会误判。
"""

import json
import sys
from datetime import date, datetime

# ---------------------------------------------------------------------------
# 法定节假日（含调休放假的周末）：填写不工作的日期
# 格式: "YYYY-MM-DD": "节日名"
# 示例: "2026-01-01": "元旦"
HOLIDAYS = {
    # TODO: 按当年国务院办公厅放假安排填入
}

# 调休上班日（本为周末但需补班的日期）
# 格式: "YYYY-MM-DD": "补班说明"
# 示例: "2026-02-28": "春节调休补班"
WORKDAY_OVERRIDES = {
    # TODO: 按当年国务院办公厅放假安排填入
}
# ---------------------------------------------------------------------------

WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def check(target: date) -> dict:
    weekday = target.weekday()
    is_weekend = weekday >= 5
    key = target.isoformat()

    holiday = HOLIDAYS.get(key)
    override = WORKDAY_OVERRIDES.get(key)

    tables_configured = bool(HOLIDAYS or WORKDAY_OVERRIDES)

    if holiday:
        action, note = "跳过", f"法定节假日：{holiday}"
    elif override:
        action, note = "触发", f"调休补班：{override}"
    elif is_weekend:
        action, note = "跳过", "周末"
    else:
        action = "触发"
        note = "常规工作日" if tables_configured else "常规工作日（节假日表未配置）"

    if not tables_configured:
        note += "；调休信息未配置，如需准确判断请更新本脚本的节假日表"

    return {
        "date": key,
        "weekday": WEEKDAY_CN[weekday],
        "is_weekend": is_weekend,
        "in_holiday_table": bool(holiday),
        "in_workday_override": bool(override),
        "action": action,
        "note": note,
    }


def main() -> None:
    if len(sys.argv) > 1:
        target = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    else:
        target = date.today()
    print(json.dumps(check(target), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
