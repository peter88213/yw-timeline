"""Provide helper functions for date/time processing.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from datetime import datetime
from datetime import timedelta


def fix_iso_dt(tlDateTime):
    """Return a date/time string with a four-number year.
    """
    if not tlDateTime.startswith('-'):
        dt = tlDateTime.split('-', 1)
        dt[0] = dt[0].zfill(4)
        tlDateTime = ('-').join(dt)

    return tlDateTime


def set_view_range(dtMin, dtMax):
    """Return maximum/minimum timestamp defining the view range in Timeline.
    """
    TIME_LIMIT = '0100-01-01 00:00:00'
    # This is used to create a time interval outsides the processible time range.

    SEC_PER_DAY = 24 * 3600

    dt = dtMin.split(' ')

    if dt[0].startswith('-'):
        startYear = -1 * int(dt[0].split('-')[1])
        # "BC" year.

    else:
        startYear = int(dt[0].split('-')[0])

    if startYear < 100:

        if dtMax == dtMin:
            dtMax = TIME_LIMIT

        return dtMin, dtMax

    # dtMin and dtMax are within the processible range.

    vrMax = datetime.fromisoformat(fix_iso_dt(dtMax))
    vrMin = datetime.fromisoformat(fix_iso_dt(dtMin))

    viewRange = (vrMax - vrMin).total_seconds()

    # Calculate a margin added to the (dtMin dtMax) interval.

    if viewRange > SEC_PER_DAY:
        margin = viewRange / 10

    else:
        margin = 3600

    dtMargin = timedelta(seconds=margin)

    try:
        vrMin -= dtMargin
        dtMin = vrMin.isoformat(' ', 'seconds')

    except OverflowError:
        pass

    try:
        vrMax += dtMargin
        dtMax = vrMax.isoformat(' ', 'seconds')

    except OverflowError:
        pass

    return dtMin, dtMax
