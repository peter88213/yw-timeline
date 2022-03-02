"""Provide helper functions for date/time processing.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw-timeline
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""


def fix_iso_dt(tlDateTime):
    """Return a date/time string with a four-number year.
    
    Positional arguments:
        tlDateTime - date/time string as read in from Timeline.
    
    This is required for comparing date/time strings, 
    and by the datetime.fromisoformat() method.
    """
    if tlDateTime.startswith('-'):
        tlDateTime = tlDateTime.strip('-')
        isBc = True
    else:
        isBc = False
    dt = tlDateTime.split('-', 1)
    dt[0] = dt[0].zfill(4)
    tlDateTime = ('-').join(dt)
    if isBc:
        tlDateTime = f'-{tlDateTime}'
    return tlDateTime
