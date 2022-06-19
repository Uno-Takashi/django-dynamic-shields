# -*- coding: utf-8 -*-

# Copyright (c) 2019, Brandon Nielsen
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

from aniso8601.builders import TupleBuilder
from aniso8601.builders.python import PythonTimeBuilder
from aniso8601.date import parse_date
from aniso8601.exceptions import ISOFormatError
from aniso8601.resolution import TimeResolution
from aniso8601.timezone import parse_timezone

def get_time_resolution(isotimestr):
    #Valid time formats are:
    #
    #hh:mm:ss
    #hhmmss
    #hh:mm
    #hhmm
    #hh
    #hh:mm:ssZ
    #hhmmssZ
    #hh:mmZ
    #hhmmZ
    #hhZ
    #hh:mm:ss±hh:mm
    #hhmmss±hh:mm
    #hh:mm±hh:mm
    #hhmm±hh:mm
    #hh±hh:mm
    #hh:mm:ss±hhmm
    #hhmmss±hhmm
    #hh:mm±hhmm
    #hhmm±hhmm
    #hh±hhmm
    #hh:mm:ss±hh
    #hhmmss±hh
    #hh:mm±hh
    #hhmm±hh
    #hh±hh

    timestr = _split_tz(isotimestr)[0]

    if timestr.count(':') == 2:
        #hh:mm:ss
        return TimeResolution.Seconds
    elif timestr.count(':') == 1:
        #hh:mm
        return TimeResolution.Minutes

    #Format must be hhmmss, hhmm, or hh
    if timestr.find('.') == -1:
        #No time fractions
        timestrlen = len(timestr)
    else:
        #The lowest order element is a fraction
        timestrlen = len(timestr.split('.')[0])

    if timestrlen == 6:
        #hhmmss
        return TimeResolution.Seconds
    elif timestrlen == 4:
        #hhmm
        return TimeResolution.Minutes
    elif timestrlen == 2:
        #hh
        return TimeResolution.Hours

    raise ISOFormatError('"{0}" is not a valid ISO 8601 time.'
                         .format(isotimestr))

def parse_time(isotimestr, builder=PythonTimeBuilder):
    #Given a string in any ISO 8601 time format, return a datetime.time object
    #that corresponds to the given time. Fixed offset tzdata will be included
    #if UTC offset is given in the input string. Valid time formats are:
    #
    #hh:mm:ss
    #hhmmss
    #hh:mm
    #hhmm
    #hh
    #hh:mm:ssZ
    #hhmmssZ
    #hh:mmZ
    #hhmmZ
    #hhZ
    #hh:mm:ss±hh:mm
    #hhmmss±hh:mm
    #hh:mm±hh:mm
    #hhmm±hh:mm
    #hh±hh:mm
    #hh:mm:ss±hhmm
    #hhmmss±hhmm
    #hh:mm±hhmm
    #hhmm±hhmm
    #hh±hhmm
    #hh:mm:ss±hh
    #hhmmss±hh
    #hh:mm±hh
    #hhmm±hh
    #hh±hh

    (timestr, tzstr) = _split_tz(isotimestr)

    if timestr[0].isdigit() is False or timestr[-1].isdigit() is False:
        raise ISOFormatError('"{0}" is not a valid ISO 8601 time.'
                             .format(timestr))

    if tzstr is None:
        tz = None
    else:
        tz = parse_timezone(tzstr, builder=TupleBuilder)

    return _RESOLUTION_MAP[get_time_resolution(timestr)](timestr, tz, builder)

def parse_datetime(isodatetimestr, delimiter='T', builder=PythonTimeBuilder):
    #Given a string in ISO 8601 date time format, return a datetime.datetime
    #object that corresponds to the given date time.
    #By default, the ISO 8601 specified T delimiter is used to split the
    #date and time (<date>T<time>). Fixed offset tzdata will be included
    #if UTC offset is given in the input string.

    isodatestr, isotimestr = isodatetimestr.split(delimiter)

    datepart = parse_date(isodatestr, builder=TupleBuilder)

    timepart = parse_time(isotimestr, builder=TupleBuilder)

    return builder.build_datetime(datepart, timepart)

def _parse_hour(timestr, tz, builder):
    #Format must be hh or hh.
    hourstr = timestr

    if hourstr == '24':
        return builder.build_time(tz=tz)

    return builder.build_time(hh=hourstr, tz=tz)

def _parse_minute_time(timestr, tz, builder):
    #Format must be hhmm, hhmm., hh:mm or hh:mm.
    if timestr.count(':') == 1:
        #hh:mm or hh:mm.
        hourstr, minutestr = timestr.split(':')
    else:
        #hhmm or hhmm.
        hourstr = timestr[0:2]
        minutestr = timestr[2:]

    return builder.build_time(hh=hourstr, mm=minutestr, tz=tz)

def _parse_second_time(timestr, tz, builder):
    #Format must be hhmmss, hhmmss., hh:mm:ss or hh:mm:ss.
    if timestr.count(':') == 2:
        #hh:mm:ss or hh:mm:ss.
        hourstr, minutestr, secondstr = timestr.split(':')
    else:
        #hhmmss or hhmmss.
        hourstr = timestr[0:2]
        minutestr = timestr[2:4]
        secondstr = timestr[4:]

    return builder.build_time(hh=hourstr, mm=minutestr, ss=secondstr, tz=tz)

def _split_tz(isotimestr):
    if isotimestr.find('+') != -1:
        timestr = isotimestr[0:isotimestr.find('+')]
        tzstr = isotimestr[isotimestr.find('+'):]
    elif isotimestr.find('-') != -1:
        timestr = isotimestr[0:isotimestr.find('-')]
        tzstr = isotimestr[isotimestr.find('-'):]
    elif isotimestr.endswith('Z'):
        timestr = isotimestr[:-1]
        tzstr = 'Z'
    else:
        timestr = isotimestr
        tzstr = None

    return (timestr, tzstr)

_RESOLUTION_MAP = {
    TimeResolution.Hours: _parse_hour,
    TimeResolution.Minutes: _parse_minute_time,
    TimeResolution.Seconds: _parse_second_time
}
