from datetime import time

# This config allows flexibility per-owner later
NORMAL_HOURS_START = time(9, 0)
NORMAL_HOURS_END = time(17, 0)
PRE_HOURS_END = time(8, 0)
AFTER_HOURS_START = time(18, 0)

def classify_requested_time(dt):
    requested_time = dt.time()

    if requested_time < PRE_HOURS_END:
        return "pre-hours"
    elif requested_time > AFTER_HOURS_START:
        return "after-hours"
    else:
        return "normal"