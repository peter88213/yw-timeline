[Project homepage](https://peter88213.github.io/yw-timeline)

------------------------------------------------------------------

Synchronize yWriter with Timeline.

## Instructions for use

### Intended usage

The included installation script creates a shortcut on the desktop. 
- If you drag a Timeline project onto it and drop it, either a new yWriter project is generated or an existing one is synchronized. 
- If you drag a yWriter project and drop it on the icon, a new timeline will be generated or an existing one will be synchronized. 

### Command line usage

Alternatively, you can

- launch the program on the command line passing the yWriter/Timeline project file as an argument, or
- launch the program via a batch file.

usage: `yw-timeline.pyw [--silent] Sourcefile`

#### positional arguments:

`Sourcefile` 

The path of the yWriter/Timeline project file.

#### optional arguments:

`--silent`  suppress error messages and the request to confirm overwriting


## Custom configuration

You can override the default settings by providing a configuration file. Be always aware that faulty entries may cause program errors or unreadable Timeline projects. If you change a configuration inbetween, previously synchronized projects might no longer match. 

### Global configuration

An optional global configuration file can be placed in the configuration directory in your user profile. It is applied to any project. Its entries override yw-timeline's built-in constants. This is the path:
`c:\Users\<user name>\AppData\Roaming\PyWriter\yw-timeline\config\yw-timeline.ini`
  
The **install.bat** installation script installs a sample configuration file containing yw-timeline's default values. You can modify or delete it. 

### Local project configuration

An optional project configuration file named `yw-timeline.ini` can be placed in your project directory, i.e. the folder containing your yWriter and Timeline project files. It is only applied to this project. Its entries override yw-timeline's built-in constants as well as the global configuration, if any.

### How to provide/modify a configuration file

The yw-timeline distribution comes with a sample configuration file located in the `sample` subfolder. It contains yw-timeline's default settings and options. This file is also automatically copied to the global configuration folder during installation. You best make a copy and edit it.

- The SETTINGS section comprises the program "constants" usually not to be changed. If you change them, the program might behave differently than described in the documentation. So only touch them if you are clear about the consequences.
- The OPTIONS section comprises options for regular program execution. 
- Comment lines begin with a `#` number sign. In the example, they refer to the code line immediately above.

This is the configuration explained: 

```
[SETTINGS]
scene_label = Scene
# Events with this label becone scenes in a newly creates yWriter project. 

item_category = Item
# Events assigned to this category become items in the yWriter project.

default_date_time = 2021-07-26 00:00:00
# Date/time stamp for imported yWriter scenes without date/time set.

scene_color = 170,240,160
# Color for events imported as scenes from yWriter.

item_color = 160,230,250
# Color for events that are assigned to the "item" category.

[OPTIONS]
ignore_items = No
# No: Synchronize items with yWriter.
# Yes: Do not synchronize items with yWriter.

ignore_unspecific = No
# No: Transfer all Scenes from yWriter to Timeline. Events assigned to scenes having no specific date/time stamp get the default date/time.
# Yes: Only transfer Scenes with a specific date/time stamp from yWriter to Timeline.

single_backup = Yes
# Yes: Overwrite existing backup file. Extension = .bak
# No: Create a new, numbered backup file. Extension = .bkxxxx

```


### How to reset the configuration to defaults

Just delete your global and local configuration files.



## Conventions

### General
- The yWriter project file and the Timeline file are located in the same directory.
- They have the same file name and differ in the file extension.
- Either a timeline or a yWriter project is generated from the other file for the first time. After that, the two files can be synchronized against each other.
- **Please keep in mind:** Synchronizing means overwriting target data with source data. Since yw-timeline works in both directions, there is always a danger of confusing source and target, thus losing changes. So if the program asks you for confirmation to overwrite a file, better check if it's actually the target file.


### On the yWriter side

#### Items
- Each item is synchronized with Timeline. Items appear in Timeline as events of the "Item" category. 
- You can add and remove "Item" events in yWriter. 
- Changes to the item short name affect the event text during synchronization.
- Changes to the item description affect the event description during synchronization.

#### Scenes
- Only normal scenes are synchronized with Timeline, or exported to Timeline. Unused scenes, "Notes" scenes, and "Todo" scenes will not show up in the timeline.
- Optionally, scenes with an unspecific time stamp (day, hours, minutes) are not transferred to the timeline.
- Scenes with an unspecific time stamp (day, hours, minutes) get a specific time stamp (date/time) when transferred from the timeline.
- Changes to the scene date/time affect the event start date/time during synchronization.
- Changes to the scene title affect the event text during synchronization.
- Changes to the scene description affect the event description during synchronization.
- Changes to the scene type may add or remove the corresponding event during synchronization.
- Adding or removing scenes will add or remove the corresponding event during synchronization.


### On the Timeline side

#### Items
- Each event of the "Item" category is synchronized with yWriter. Such events appear in yWriter as items. Although the date/time stamps of these special events are not visible in yWriter, they determine the order in yWriter's item list.
- An item ID is a string looking like "ItemID:1". It is auto-generated and must not be changed manually.
- An "Item category" event can not be a "Scene" event at the same time. When creating a new yWriter project from a timeline, the "Item" category has priority over the "Scene" label.
- You can add and remove "Item" events in Timeline. 
- Changes to the event text affect the item short name during synchronization.
- Changes to the event description affect the item description during synchronization.

#### Scenes
- A scene ID is a string looking like "ScID:1". It is auto-generated and must not be changed manually.
- Only events with a label containing the string "Scene" (user input) or a scene ID (auto-generated) are exported as scenes to a new yWriter project.
- When generating a new yWriter project from a timeline the first time, "Scene" labels are replaced with scene ID labels.
- If a new yWriter project is generated again with the same timeline, the scene ID labels may change.
- Only events with a label containing a scene ID are synchronized with an existing yWriter project.
- Changes to the event start date/time affect the scene date/time during synchronization.
- Changes to the event text affect the scene title during synchronization.
- Changes to the event description affect the scene description during synchronization.
- The scene structure of an existing yWriter project can not be changed in Timeline. Adding/removing events, or adding/removing scene IDs from event labels will *not* add or remove the corresponding scene during synchronization. 

### Known limitations

- Scene events that begin before 0100-01-01 in the timeline, will not be synchronized with yWriter, because yWriter can not handle these dates. The same applies to the scene duration in this case, i.e. the event duration in Timeline and the scene duration in yWriter may differ.
- If a scene event ends after 9999-12-31 in the timeline, the scene duration is not synchronized with yWriter.


## Installation path

The **install.bat** installation script installs *yw-timeline.pyw* in the user profile. This is the installation path: 

`c:\Users\<user name>\AppData\Roaming\PyWriter\yw-timeline`
    