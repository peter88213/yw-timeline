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



## Installation path

The **install.bat** installation script installs *yw-timeline.pyw* in the user profile. This is the installation path: 

`c:\Users\<user name>\AppData\Roaming\PyWriter\yw-timeline`
    