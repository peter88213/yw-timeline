[Project home page](index) > Changelog

------------------------------------------------------------------------

## Changelog

### Planned features

See the [GitHub "features" project](https://github.com/peter88213/yw-timeline/projects/1).

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

### v0.6.1 Alpha bugfix release

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

