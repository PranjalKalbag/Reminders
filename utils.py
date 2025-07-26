from dateutil.rrule import rrulestr
from datetime import datetime, date

def matches_rrule(rrule_str: str, start_date: date, target_date: date) -> bool:
    rule = rrulestr(rrule_str, dtstart=datetime.combine(start_date, datetime.min.time()))
    return any(d.date() == target_date for d in rule.between(
        datetime.combine(target_date, datetime.min.time()),
        datetime.combine(target_date, datetime.max.time()),
        inc=True
    ))

def rrule_matches_range(rrule_str: str, dt_start: date, range_start: date, range_end: date) -> bool:
    try:
        rule = rrulestr(rrule_str, dtstart=datetime.combine(dt_start, datetime.min.time()))
        occurrences = rule.between(
            datetime.combine(range_start, datetime.min.time()),
            datetime.combine(range_end, datetime.max.time()),
            inc=True
        )
        return len(occurrences) > 0
    except Exception as e:
        return False