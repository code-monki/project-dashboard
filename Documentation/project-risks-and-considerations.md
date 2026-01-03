# Project Risks and Considerations

This document outlines potential risks, challenges, and open questions for the Project Dashboard concept. The goal is to think through these issues before starting development to create a more robust design.

## 1. Execution and Feedback

- **Error Handling:** How should the UI report script failures? Should it just show the `stderr` output, or provide a more user-friendly notification?
  
  The UI should have a view at the bottom of the main window that essentially acts as a read-only terminal that allows the user to copy text if needed. In the TUI the user may or may not have a color terminal so where in the GUI we can use color-coding to make warnings and errors stand out, that may be more challenging in a TUI. In an ideal situation this would be a tabbed interface that can separate the warnings and errors into tabs that are separate from the main execution output.
  
- **Long-Running Tasks:** How will the application handle scripts that run for a long time (e.g., a "watch" task or a development server)? The UI needs to remain responsive and show that the task is still running.

  The application will need a watcher to determine when tasks have completed. This also implies the need for a button to cancel execution if the user so desires.
  
- **Task State:** Should the application prevent a user from running the same target multiple times concurrently? Or is that a valid use case?

  Honestly, my thinking is that the app config file would be on a project by project basis so it is unlikely that a user would attempt to run the same target back to back. That being said, we can disable the ability launch more than one "build" operation at a time. We may want to consider offering the ability to chain operations, i.e,. make clean && make all && make dist as a workflow option. The only use case that I can think of where more than one build operation would be launched would be where there are no dependencies for a target. For example, make docs would likely have nothing to do with a full build on the application and could be run concurrently. That being the case we would want to allow the user to have the final say on what is and isn't concurrently launched although we do want to not allow launching the same target concurrently. This may require some sort of lock file, etc., written to disk to ensure the behavior cannot occur.
  
- **Output Display:** Where will the `stdout` and `stderr` from scripts be displayed? In a dedicated pane within the app? A new terminal window? A temporary pop-up?

  See the comments on error-handling.
  
- **Interactive Scripts:** How will the application handle scripts that require interactive user input (e.g., via `read` in shell or `prompt` in Node.js)?

  That's the tricky one. Ideally we could intercept the prompt and display it to the user in a dialog. If that is not feasible, then we could embed a "terminal" tab in the display discussed in error-handling.

## 2. Security

- **Command Injection:** The application will execute commands defined in project files. This is a potential security risk. Should the application have a "trust" system for projects, where the user explicitly approves the project directory before any commands can be run?

  I'm not sure this is a big issue for this application. The application will only read and execute from user-defined files. I'm open to discussing this point further.
  
- **Environment Variables:** Scripts often rely on environment variables. How will the application ensure it runs commands with the same environment as the user's configured shell (`.bashrc`, `.zshrc`, etc.)?

  On Unix-based operating systems, I believe the application can spawn or fork a process and source the user's .bashrc/.zshrc for the process (correct me if I'm misremembering).
  
  I haven't worked extensively with Windows for several decades now so I'm not conversant with how that operating system handles that sort of thing. I'm fine being educated/advised on that front.

## 3. Usability and User Experience (UX)

- **Target Organization:** For large projects, the list of targets could become very long. How should they be organized? Alphabetically? Grouped by the file they came from (`Makefile`, `package.json`)? Should users be able to create their own custom groups?

  Users should be able to define custom groups and assign targets to those groups. They shoud also be allowed to set the order of those groups.

- **Configuration vs. Convention:** How much should be configurable versus relying on sensible defaults? For example, should the "help" target in a Makefile be hardcoded as `help`, or should the user be able to specify a different target name?

  I would default to looking for a help target in makefiles. If it is not there, I would suggest prompting the user to determine if there is an equivalent target. If the user says there is not one, then a list of "top-level" targets should be presented in a checkbox list for the user to select from.
  
  This same thinking may have to hold true for package.json targets and certainly for any scripts that are detected.
  
  From a convention perspective, I'd suggest that scripts should be in a folder at the top-level of the repo and that folder should be named "scripts". However, we may need to provide a file finder so that the user can pick and choose targets as necessary.
  
- **Onboarding:** How does a user get started with a new project? Is the initial scan automatic, or does the user have to trigger it manually?

  1. User opens application
  2. User selects project folder
  3. If there is a dashboard config file, load it.
  4. If there is not a dashboard config file, scan the folder and its children for build artifacts (makefiles, package.json, etc.) and present a list of the items found so that the user can pick and choose what is relevant for them.


## 4. Discovery and Syncing

- **Configuration Drift:** What happens if the configuration file gets out of sync with the actual build files (e.g., a script is renamed or deleted)? Should there be a manual "refresh" button? Should the app automatically watch for changes?

  The application can monitor for name changes / deletions of the files it knows about. The application can offer a "refresh" button to do a rescan which will result in the user validating what is / is not relevant. If the user is using groups, they will need to be select the group for any new/changed items. This might be best accomplished with a grid-like display where the first column is a checkbox for Add, the next is the target / script name, and the last column might be the group. That's just off the top and will need more analysis to determine the best UI design when we get to design.

- **Nested Projects:** How will the dashboard handle monorepos or projects with nested `package.json` or Makefiles? Should it show a single unified list of targets, or a tree-like structure?

  Tree-like structure wins every time. it's more descriptive with regard to project/file structure.
  
## 5. Cross-Platform and Environment Issues

- **Shell Differences:** Different operating systems and users have different default shells (`bash`, `zsh`, `fish`, `PowerShell`, etc.). The application needs to be aware of which shell to use for executing commands.

    Can't vouch for Windows, but the shell is easily identified via echo $SHELL in Unix-based operating systems. Windows has the Powershell, WSL, and cmd.exe, but I'm not sure what the best approach there would be.
    
- **Path and Separator Issues:** Ensuring that paths and command separators work correctly across Windows, macOS, and Linux is a common challenge.

  This is actually slightly easier because Windows may not provide a make utility. I know it has nmake and can run other make utilities in WSL (such as GNU Make). That may be an issue where we have to prompt the user for that information.
  
  Unix is easier in that respect so Linux, MacOS, FreeBSD, etc. will all work pretty much the same.
  
  I'm open to being educated on how best to handle that for Windows as previously mentioned, I haven't spent much time there in a long time.