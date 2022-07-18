[Project homepage](https://peter88213.github.io/yw-timeline)

------------------------------------------------------------------

Synchronize yWriter with Timeline.

## Instructions for use

### Intended usage

After installation, create a shortcut on the desktop. 
- If you drag a Timeline project onto it and drop it, either a new yWriter project is generated or an existing one is synchronized. 
- If you drag a yWriter project and drop it on the icon, a new timeline is generated or an existing one is synchronized. 

### Context menu (Windows only)

Under Windows, you optionally can launch *yw-timeline* via context menu.

After installation, you can add the context menu entries by double-clicking  `add_context_menu.reg`. 
You may be asked for approval to modify the Windows registry. Please accept.

- On right-clicking a *.yw7* file, an *Export to Timeline* option appears.
- On right-clicking a *.timeline* file, an *Export to yWriter* option appears.

You can remove the context menu entries by double-clicking  `rem_context_menu.reg`.

Please note that these context menus depend on the currently installed Python version. After a major Python update you may need to run the setup program again and renew the registry entries.

### Launch from novelyst

If [novelyst](https://peter88213.github.io/novelyst/) is installed, the setup script offers the installation of a *Timeline* plugin.
The plugin adds a *Timeline* submenu to the *novelyst* main menu. The submenu has the following entries:

- Information (compare yWriter and timeline file dates)
- Update timeline from yWriter
- Update yWriter from timeline
- Edit timeline (launch Timeline)

If you install *novelyst* at a later time, you can always install the plugin afterwards by running the *yw-timeline* setup script again.

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
`c:\Users\<user name>\.pywriter\yw-timeline\config\yw-timeline.ini`
  
The setup script installs a sample configuration file containing yw-timeline's default values. You can modify or delete it. 

### Local project configuration

An optional project configuration file named `yw-timeline.ini` can be placed in your project directory, i.e. the folder containing your yWriter and Timeline project files. It is only applied to this project. Its entries override yw-timeline's built-in constants as well as the global configuration, if any.

### How to provide/modify a configuration file

The yw-timeline distribution comes with a sample configuration file located in the `sample` subfolder. It contains yw-timeline's default settings and options. This file is also automatically copied to the global configuration folder during installation. You best make a copy and edit it.

- The SETTINGS section comprises the program "constants". If you change them, the program might behave differently than described in the documentation. So only touch them if you are clear about the consequences.
- The OPTIONS section comprises options for regular program execution. 
- Comment lines begin with a `#` number sign. In the example, they refer to the code line immediately above.

This is the configuration explained: 

```
[SETTINGS]

scene_label = Scene

# Events with this label become scenes in a newly created 
# yWriter project. 

default_date_time = 2021-07-26 00:00:00

# Date/time stamp for imported yWriter scenes without
# date/time set. When converting between specific
# date/time and unspecific D/H/M, this time stamp is used
# as a reference.

scene_color = 170,240,160

# Color for events imported as scenes from yWriter.

[OPTIONS]

ignore_unspecific = No

# No:  Transfer all Scenes from yWriter to Timeline. Events
#      assigned to scenes having no specific date/time stamp
#      get the default date plus the unspecific 'D' as start
#      date, and 'H':'M' as start time.
# Yes: Only transfer Scenes with a specific date/time stamp
#      from yWriter to Timeline.

dhm_to_datetime = No

# Yes: Convert yWriter unspecific D/H/M to specific date/time
#      when synchronizing from Timeline.
#      Use the date from default_date_time as a reference.
#      Time is 'H':'M'.
# Precondition:
#      datetime_to_dhm = No

datetime_to_dhm = No

# Yes: Convert yWriter spcific date/time to unspecific D/H/M
#      when synchronizing from Timeline. Use the date from
#      default_date_time as a reference. H, M are taken from
#      the scene time.
# Precondition:
#      dhm_to_datetime = No

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

- Only normal scenes are synchronized with Timeline, or exported to Timeline. Unused scenes, "Notes" scenes, and "Todo" scenes will not show up in the timeline.
- Optionally, scenes with an unspecific time stamp (day, hours, minutes) are not transferred to the timeline.
- Changes to the scene date/time affect the event start date/time during synchronization.
- Changes to the scene title affect the event text during synchronization.
- Changes to the scene description affect the event description during synchronization.
- Changes to the scene type may add or remove the corresponding event during synchronization.
- Adding or removing scenes will add or remove the corresponding event during synchronization.


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

### Synchronization of unspecific date/time in yWriter with specific date/time in Timeline.

Day/Hour/Minute is converted to specific Timeline start/end date/time stamps, using the duration and the default date/time.

The other way around (Timeline to yWriter), there are three options:

- Retain each scene's date/time mode (default).
- Overwrite D/H/M with specific date/time stamps (**dhm_to_datetime** option).
- Convert specific Timeline date/time stamps to D/H/M (**datetime_to_dhm** option)

D/H/M refers to the default date/time stamp that can be set in the configuration.


### Known limitations

- Scene events that begin before 0100-01-01 in the timeline, will not be synchronized with yWriter, because yWriter can not handle these dates.
- The same applies to the scene duration in this case, i.e. the event duration in Timeline and the scene duration in yWriter may differ.
- Scenes that begin before 0100-01-01 in the timeline, can not have the D/H/M information converted to a date/time stamp and vice versa.
- If a scene event ends after 9999-12-31 in the timeline, the scene duration is not synchronized with yWriter.


## Installation path

The setup script installs *yw-timeline.pyw* in the user profile. This is the installation path on Windows: 

`c:\Users\<user name>\.pywriter\yw-timeline`
    