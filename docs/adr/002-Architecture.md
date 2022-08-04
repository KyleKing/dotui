# Architecture

## General

Build with an MVP-like model:

- Model: interchangeable and standard interface for the dotfile manager
    - Implementation wraps the relevant CLI tool for a consistent interface
    - Would have a configurable enum that initially supports yadm, but could be extended for most others
        - Would accept user contributions of new implementations by adding a subdirectory to `dotui/plugins/<tool_name>` (Stow, Plain Git, etc.)
- Presenter: Manipulate Model data for the formats to one that can be easily shown in the View
- View: The Widgets!

## UI Components

- **Project Status** - From model, create a dictionary with keys for Push, Pull, and Modified
    - Refreshes on regular interval, such as 20s
    - May also have an editable configuration as part of this screen
- **Tree View** - Create dictionary of Full Path and Modified Status
    - Could be useful to know if the file is symlinked or a template
- **Diff View** - Need path to the file, the local and upstream versions, and some data about the diff
    - Need to determine how the diff data should be structured and what library to use
- **Template View** - at Presenter level, this is just a diff between the created and the template file
    - Model will need to provide a set of tuples for template and generated file, but the UI will naively determine the diff
    - Would likely have a function in the Model to regenerate the templated file, which would refresh the view

## Other

- See guidance on [environment variables](https://0x46.net/thoughts/2019/02/01/dotfile-madness/) to use for selecting where to store the `dotui` configuration file
