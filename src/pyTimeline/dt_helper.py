"""Provide a helper function for date/time processing.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""


def fix_iso_dt(tlDateTime):
    """Return a date/time string with a four-number year.
    """
    if not tlDateTime.startswith('-'):
        dt = tlDateTime.split('-', 1)
        dt[0] = dt[0].zfill(4)
        tlDateTime = ('-').join(dt)

    return tlDateTime
