[Project home page](index) > Changelog

------------------------------------------------------------------------

## Changelog

### Planned features

See the [GitHub "features" project](https://github.com/peter88213/yw-timeline/projects/1).

### v1.4.1

- Set own window icon.

Based on PyWriter v7.4.1

### v1.4.0 

- Handle the exception occurring when converting a yWriter project with no scene.
- Add internationalization according to GNU coding standards.
- Provide German localization.

Based on PyWriter v7.2.1

### v1.2.4 Update setup script

- Change the working dir to the script dir on startup in order to avoid "file not found" error.

Based on PyWriter v5.18.0

### v1.2.3 Improved setup

- Catch exceptions in the setup script.

Based on PyWriter v5.18.0

### v1.2.2 Improved word counting

- Fix word counting considering ellipses.

Based on PyWriter v5.12.4

### v1.2.1 Improved word counting

- Fix word counting considering comments, hyphens, and dashes.

Based on PyWriter v5.12.3

### v1.2.0

- Provide a novelyst plugin.

Based on PyWriter v5.6.1

### v1.0.2 Bugfix release

- Fix a bug where characters and locations and items are multiplied when exporting to yWriter

Based on PyWriter v5.6.0

### v1.0.1

- Improve code and documentation quality.

Based on PyWriter v5.0.3

### v1.0.0

- Rework the user interface. 
- Refactor the code.

Based on PyWriter v5.0.0

### v0.20.5 Create backup when overwriting

- Create registry files on setup only under Windows.
- Remove the "single backup" option.

Based on PyWriter v3.30.0

### v0.20.4 Support non-Windows OS

- Move installation and configuration to another location (see instructions for use).

Based on PyWriter v3.28.1

### v0.20.3 Enable non-Windows operation 

- Catch an exception that is thrown when evaluating a Windows environment variable under a non-Windows OS.

Based on PyWriter v3.28.1

### v0.20.2 Beta release

- Undo a change made just for debugging.

Based on PyWriter v3.26.1

### v0.20.1 Beta release

- Fix a bug where events lose or change their category or container on sync.

Based on PyWriter v3.26.1

### v0.20.0 Beta release

- Abandon "item" processing to make the configuration clearer and the code more maintainable.
- Change the default value for invalid date from "-0001-01-01" to
"0001-01-01" in order to avoid isoformat errors.

Based on PyWriter v3.24.3

### v0.18.0 Update for Timeline 2.5

- Adapt the Timeline XML file structure. Downward compatible with Timeline 2.4.

Based on PyWriter v3.24.3

### v0.16.1 Bugfix release

- Fix a bug causing an exception when a new item is added to a scene.

Based on PyWriter v3.18.1

### v0.16.0 Beta - Feature complete

Synchronize unspecific date/time in yWriter with specific date/time in Timeline.

D/H/M is converted to specific Timeline start/end date/time stamps, using the duration and the default date/time.

The other way around (Timeline to yWriter), there are three options:

- Retain each scene's date/time mode (default).
- Overwrite D/H/M with specific date/time stamps (dhm_to_datetime option).
- Convert specific Timeline date/time stamps to D/H/M (datetime_to_dhm option)

Based on PyWriter v3.16.3

### v0.14.0 Alpha - New feature

Set the view range in new and synchronized timelines.

Based on PyWriter v3.16.1

### v0.12.5 Alpha - Optional update

Major Refactoring.

Based on PyWriter v3.16.1

### v0.12.4 Alpha - Optional update

Major Refactoring.

Based on PyWriter v3.16.1

### v0.12.3 Alpha - Optional update

- Use standardlib methods in TlFile.write() for converting iso date/time stamps.  

Based on PyWriter v3.16.0

### v0.12.2 Alpha - Optional update

- Use standardlib methods in TlFile.read() for converting iso date/time stamps.  

Based on PyWriter v3.16.0

### v0.12.1 Alpha - No automatic shortcut creation

- Due to sporadic security warnings, the automatic shortcut creation during installation is removed. The user is now guided to create the application shortcut manually.  

Based on PyWriter v3.16.0

### v0.12.0 Alpha - Handle time periods

- When converting to yWriter, calculate the duration and store it in the yWriter scene metadata.
- When converting to Timeline, calculate the end date from the scene duration.

Based on PyWriter v3.16.0

### v0.10.2 Alpha - Handle two-figure years

- When synchronizing with yWriter, prevent two-figure years from being "completed".

Ywriter prefixes two-figure years automatically with "19" or "20", so do not synchronize dates below the year 100.

Based on PyWriter v3.16.0

### v0.10.1 Alpha - Do not change "BC" dates

- When synchronizing with yWriter, "BC" dates remain unchanged.

"BC" Dates are stored in Timeline with a negative sign. Such dates are changed by yWriter to 0001-01-01, since it apparently can't handle negative dates. In order to preserve "BC" Dates in Timeline when synchronizing, date/time information is not overwritten, if yWriter's scene date is 0001-01-01. 

Based on PyWriter v3.16.0

### v0.10.0 Alpha - Add "ignore unspecific" option

- Implement an option to synchronize only scenes with a specific date/time set. 

Based on PyWriter v3.16.0

### v0.8.1 Alpha - Handle containers

- Opening brackets at scene title start are prefixed with ' ' in the timeline. Thus, the masking of leading brackets is invisible in Timeline as well.

Based on PyWriter v3.16.0

### v0.8.0 Alpha - Handle containers

- Containers are invisible in yWriter.
- Brackets at scene title start are prefixed with '_' in the timeline.

Based on PyWriter v3.16.0

### v0.6.2 Alpha bugfix release

- Fix a bug (uninitialized variable).

Based on PyWriter v3.16.0

### v0.6.1 Alpha 

- Back up target files. Note: Backups are created even if the synchronization process is cancelled.

Based on PyWriter v3.16.0

### v0.6.0 Alpha 

- Read configuration from INI file.

Based on PyWriter v3.14.0

### v0.4.2 Alpha bugfix release

- Fix a bug deleting the scene ID if an event is assigned to any category.

Based on PyWriter v3.12.9

### v0.4.1 Alpha bugfix release

- Fix a bug causing multiple "Item" category entries.

Based on PyWriter v3.12.9

### v0.4.0 Alpha release

- Fix faulty regular expressions causing scene IDs not to be unique.
- Make sure that subsequently added event descriptions are inserted at the right position in the Timeline XML tree.
- Delete event description during synchronization, if the corresponding scene description is empty.
- Color events that are linked to scenes mint green.
- Synchronize items with yWriter. Items are mapped to events with category "Item" (light blue). 

Based on PyWriter v3.12.9

### v0.2.0 Limited alpha release

- Synchronization works only one-way: In order to avoid damage, existing timelines are not overwritten due to [critical bugs yet to be fixed](https://github.com/peter88213/yw-timeline/issues). 

Based on PyWriter v3.12.9

### v0.1.7 Alpha bugfix release

- Provisionally fix a bug making a Timeline project not processible for the application, if all events have the same date/time.

Based on PyWriter v3.12.9

### v0.1.6 Alpha test release

- Refactor.
- Update help text.

Based on PyWriter v3.12.9

### v0.1.5 Alpha test release

- Fix updating Timeline from yWriter.
- Filter normal scenes.

Based on PyWriter v3.12.9

### v0.1.4 Alpha test release

- Updating yWriter from Timeline works.
- Processing of end date/time and scene duration is missing.

Known bugs:
- When updating Timeline from yWriter, non-scene events are deleted.

Based on PyWriter v3.12.9

### v0.1.3 Alpha test release

- Generate a new yWriter project from a Timeline works.
- Generate a new Timeline from a yWriter project works.
- Synchronization has to be fixed.
- Processing of end date/time and scene duration is missing.

Based on PyWriter v3.12.9

