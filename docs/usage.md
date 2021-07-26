[Project homepage](https://peter88213.github.io/yw-timeline)

------------------------------------------------------------------

Synchronize yWriter with Timeline.

## Conventions

### General
- The yWriter project file and the Timeline file are located in the same directory.
- They have the same file name and differ in the file extension.
- Either a timeline or a yWriter project is generated from the other file for the first time. After that, the two files can be synchronized against each other.


### On the yWriter side
- Only normal scenes are synchronized with Timeline, or exported to Timeline. Unused scenes, "Notes" scenes, and "Todo" scenes will not show up in the timeline.
- Changes to the scene date/time affect the event start date/time during synchronization.
- Changes to the scene title affect the event text during synchronization.
- Changes to the scene description affect the event description during synchronization.
- Changes to the scene type may add or remove the corresponding event during synchronization.
- Adding or removing scenes will add or remove the corresponding event during synchronization.
- Synchronizing scenes with Timeline events may switch the date/time mode to "Specific Date/Time".


### On the Timeline side
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

- Events that are linked with scenes can not be periods at the time. Only the start date/time is synchronized with yWriter.


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



## Installation path

The **install.bat** installation script installs *yw-timeline.pyw* in the user profile. This is the installation path: 

`c:\Users\<user name>\AppData\Roaming\PyWriter\yw-timeline`
    