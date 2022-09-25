import re

from .constants import BLOODPRESSURE_REGEX_PATTERN


def parse_bloodpressure_message(message: str) -> str:
    match = re.match(BLOODPRESSURE_REGEX_PATTERN, message)
    if match is None:
        return
    systolic = match.group(1)
    diastolic = match.group(2)
    heart_beat = match.group(3)
    if heart_beat:
        heart_beat = match.group(4)
    return systolic, diastolic, heart_beat