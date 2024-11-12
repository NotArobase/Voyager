import datetime as _datetime
from .constants import DAYS_PER_WEEK as DAYS_PER_WEEK, FRIDAY as FRIDAY, HOURS_PER_DAY as HOURS_PER_DAY, MINUTES_PER_HOUR as MINUTES_PER_HOUR, MONTHS_PER_YEAR as MONTHS_PER_YEAR, SATURDAY as SATURDAY, SECONDS_PER_DAY as SECONDS_PER_DAY, SECONDS_PER_HOUR as SECONDS_PER_HOUR, SECONDS_PER_MINUTE as SECONDS_PER_MINUTE, THURSDAY as THURSDAY, TUESDAY as TUESDAY, WEDNESDAY as WEDNESDAY, WEEKS_PER_YEAR as WEEKS_PER_YEAR, YEARS_PER_CENTURY as YEARS_PER_CENTURY, YEARS_PER_DECADE as YEARS_PER_DECADE
from .date import Date
from .datetime import DateTime as DateTime
from .duration import Duration as Duration
from .helpers import format_diff as format_diff, get_locale as get_locale, set_locale as set_locale, set_test_now as set_test_now, test as test, week_ends_at as week_ends_at, week_starts_at as week_starts_at
from .parser import parse as parse
from .period import Period
from .time import Time
from .tz import PRE_TRANSITION as PRE_TRANSITION, TRANSITION_ERROR as TRANSITION_ERROR, set_local_timezone as set_local_timezone, test_local_timezone as test_local_timezone, timezones as timezones
from .tz.timezone import Timezone as _Timezone
from typing import Optional, Union

def datetime(year: int, month: int, day: int, hour: int=..., minute: int=..., second: int=..., microsecond: int=..., tz: Optional[Union[str, float, _Timezone]]=..., dst_rule: str=...) -> DateTime: ...
def local(year: int, month: int, day: int, hour: int=..., minute: int=..., second: int=..., microsecond: int=...) -> DateTime: ...
def naive(year: int, month: int, day: int, hour: int=..., minute: int=..., second: int=..., microsecond: int=...) -> DateTime: ...
def date(year: int, month: int, day: int) -> Date: ...
def time(hour: int, minute: int=..., second: int=..., microsecond: int=...) -> Time: ...
def instance(dt: _datetime.datetime, tz: Optional[Union[str, _Timezone]]=...) -> DateTime: ...
def now(tz: Optional[Union[str, _Timezone]]=...) -> DateTime: ...
def today(tz: Union[str, _Timezone]=...) -> DateTime: ...
def tomorrow(tz: Union[str, _Timezone]=...) -> DateTime: ...
def yesterday(tz: Union[str, _Timezone]=...) -> DateTime: ...
def from_format(string: str, fmt: str, tz: Union[str, _Timezone]=..., locale: Optional[str]=...) -> DateTime: ...
def from_timestamp(timestamp: Union[int, float], tz: Union[str, _Timezone]=...) -> DateTime: ...
def duration(days: float=..., seconds: float=..., microseconds: float=..., milliseconds: float=..., minutes: float=..., hours: float=..., weeks: float=..., years: float=..., months: float=...) -> Duration: ...
def period(start: DateTime, end: DateTime, absolute: bool=...) -> Period: ...
