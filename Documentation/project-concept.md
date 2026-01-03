# Project Dashboard Concept

## Problem Statement

One of the issues often encountered by developers is keeping track of the various build targets associated with makefiles and Node package.json scripts. While small projects may have a manageable number of targets (< 10), larger projects, especially those with sub-project makefiles, become increasingly difficult to manage. This situation provides an opportunity to improve productivity by providing a UI-based interface that can display the build options available to the developer. The primary interface will be a GUI, with the potential for a TUI (Terminal User Interface) for terminal-only environments.

While there are plug-ins for IDEs like Visual Studio Code, developers who work primarily from the command line (terminal) may find this project of use as the developer can add notes to provide a better explanation of the target if desired.

The Project Dashboard provide the following features:

- Initial setup will recurse through project folders to discover build artifacts. It will use conventions (e.g., `make help`, `npm run`) to parse targets and will allow users to manually select scripts for inclusion.
- The application will store target metadata, including the execution path and command, to ensure the correct context when a target is run.
- Allow the user to select a target to execute with a single button-click.
- Allow the user to add/modify/remove targets after initial ingestion. This includes a freeform text input for customizing commands.
- Allow the user to add notes/explanations as metadata for a target, which can be displayed on demand.
- The UI will be generated from a configuration file upon application startup or when the file changes.

## Architectural and Technical Considerations

### User Interface

The primary user interface will be a graphical one (GUI), as most developers work within a desktop environment. However, a command-line switch could enable a Terminal User Interface (TUI) for users in SSH sessions or other terminal-only environments. The application could potentially auto-detect the environment and select the appropriate interface.

### Target Discovery and Parsing

Parsing build files is a significant challenge. The initial approach will be:
- **Makefiles:** Assume a `help` target exists that prints available targets. This is a common convention that avoids the complexity of full Makefile parsing.
- **package.json:** Use `npm run` to list available scripts.
- **Shell Scripts:** Present a list of discovered script files and allow the user to select which ones to include as executable targets.

### Data Persistence

A human-readable configuration file will be used to persist the discovered targets and user customizations. Candidates for the format include YAML, TOML, or JSON, as they are easy to parse and can be manually edited by power users if needed. This file will serve as the single source of truth for the application's UI.

### Core Architecture

The application will be designed with a common core logic layer written in a language that can support both GUI and TUI front-ends. This core will handle file discovery, parsing, configuration management, and command execution. The UI layers (GUI and TUI) will be built on top of this core, ensuring consistent behavior across both interfaces.

Ideally the application can be run on MacOS, Linux, and Windows.