# Requirements Traceability Matrix (RTM)

**Version 1.0**

**Date:** 2026-01-02

---

## 1. Purpose

This document provides a mapping between the project requirements (as defined in the SRS and `features-and-acceptance-criteria.md`) and the test cases designed to verify them. This ensures that every requirement has corresponding test coverage.

## 2. Traceability Matrix

| Requirement ID | Requirement Description | Test Case ID(s) |
| :--- | :--- | :--- |
| **E1: Project Initialization & Target Discovery** | | |
| F1.1.1 | Presents a mechanism to select a directory. | `UT-FS-01`, `ST-GUI-01`, `ST-TUI-01` |
| F1.1.2 | Searches for a configuration file. | `UT-CS-01`, `IT-PROJ-01` |
| F1.1.3 | Loads configuration file if found. | `UT-CS-02`, `IT-PROJ-02`, `ST-GUI-02` |
| F1.1.4 | Proceeds to discovery if not found. | `IT-PROJ-03`, `ST-GUI-03` |
| F1.2.1 | Scan is triggered automatically. | `IT-PROJ-03`, `ST-GUI-03` |
| F1.2.2 | Scan is recursive. | `UT-DS-01`, `IT-DISC-01` |
| F1.2.3 | Parses `Makefile` help output. | `UT-DS-02`, `IT-DISC-02` |
| F1.2.4 | Parses `package.json` scripts. | `UT-DS-03`, `IT-DISC-03` |
| F1.2.5 | Lists shell scripts. | `UT-DS-04`, `IT-DISC-04` |
| F1.2.6 | Presents discovered targets to user. | `ST-GUI-04`, `ST-TUI-02` |
| **E2: Target Execution & Feedback** | | |
| F2.1.1 | UI provides a "Run" mechanism. | `ST-GUI-05`, `ST-TUI-03` |
| F2.1.2 | Executes command in correct directory. | `UT-ES-01`, `IT-EXEC-01` |
| F2.1.3 | Prevents concurrent execution of same target. | `UT-ES-02`, `IT-EXEC-02`, `ST-GUI-06` |
| F2.1.4 | Allows concurrent execution of different targets. | `UT-ES-03`, `IT-EXEC-03`, `ST-GUI-07` |
| F2.2.1 | Dedicated output pane is present. | `ST-GUI-08`, `ST-TUI-04` |
| F2.2.2 | Output pane has tabbed views. | `ST-GUI-09` |
| F2.2.3 | `stderr` is color-coded. | `ST-GUI-10` |
| F2.2.4 | User can copy text from output. | `ST-GUI-11`, `ST-TUI-05` |
| F2.3.1 | UI indicates when a task is running. | `ST-GUI-12`, `ST-TUI-06` |
| F2.3.2 | UI provides a cancel mechanism. | `UT-ES-04`, `IT-EXEC-04`, `ST-GUI-13` |
| F2.3.3 | UI remains responsive. | `ST-GUI-14` |
| **E3: Configuration Management** | | |
| F3.1.1 | Configuration is saved to file. | `UT-CS-03`, `IT-CONF-01` |
| F3.1.2 | Format is human-readable. | `IT-CONF-02` |
| F3.2.1 | Add a new custom target. | `ST-GUI-15` |
| F3.2.2 | Edit an existing target. | `ST-GUI-16` |
| F3.2.3 | Remove a target. | `ST-GUI-17` |
| F3.3.1 | Monitors source files for changes. | `IT-PROJ-04` |
| F3.3.2 | Manual "Refresh" button. | `ST-GUI-18` |
| F3.3.3 | Prompts user to add new targets. | `ST-GUI-19` |
| F3.3.4 | Flags orphaned targets. | `ST-GUI-20` |
| **E4: UI: Target Organization** | | |
| F4.1.1 | Manage groups (create, rename, delete). | `ST-GUI-21` |
| F4.1.2 | Assign target to a group. | `ST-GUI-22` |
| F4.1.3 | Control group display order. | `ST-GUI-23` |
| F4.1.4 | Tree-like structure for nested projects. | `ST-GUI-24` |
| F4.2.1 | Edit and view notes for a target. | `ST-GUI-25` |
| F4.2.2 | View notes in a pop-up/pane. | `ST-GUI-26` |
| **E5: UI: Dual Interface (GUI/TUI)** | | |
| F5.1.1 | Launches in GUI mode by default. | `ST-GUI-27` |
| F5.1.2 | All features accessible in GUI. | `UAT-GUI-01` |
| F5.2.1 | Launches in TUI mode via flag. | `ST-TUI-07` |
| F5.2.2 | TUI is usable in standard terminal. | `UAT-TUI-01` |
| F5.2.3 | All core features accessible in TUI. | `UAT-TUI-02` |
| **E6: Cross-Platform Support** | | |
| F6.1.1 | Sources profile on Unix-like systems. | `IT-EXEC-05` |
| F6.1.2 | Uses correct environment on Windows. | `IT-EXEC-06` |
| F6.2.1 | Detects `$SHELL` on Unix-like systems. | `IT-EXEC-07` |
| F6.2.2 | Provides shell selection on Windows. | `ST-GUI-28` |
| F6.2.3 | Persists chosen shell in config. | `IT-CONF-03` |
| **NFRs** | | |
| NFR-P1 | UI remains responsive. | `ST-GUI-14` |
| NFR-P2 | Initial scan performance. | `PT-01` |
| NFR-U1 | Intuitive onboarding. | `UAT-ONBOARD-01` |
| NFR-U2 | Clear error messages. | `UAT-ERROR-01` |
| NFR-U3 | WCAG 2.1 AA Conformance. | `UAT-A11Y-01` |
| NFR-R1 | No crash on script failure. | `ST-GUI-29` |
| NFR-R2 | Robust concurrency prevention. | `ST-GUI-06` |
| NFR-S1 | Request confirmation for untrusted project. | `ST-GUI-30` |
| NFR-D1 | Integrated help system. | `ST-GUI-31`, `ST-TUI-08` |
| NFR-D2 | Comprehensive user manual. | `DOC-01` |
| NFR-D3 | Cheatsheet / Quick reference. | `DOC-02` |
| NFR-M1 | In-file documentation standard. | `CR-01` |
| NFR-M2 | Function signature documentation standard. | `CR-02` |

---
### Test Case ID Prefixes
- **UT:** Unit Test
- **IT:** Integration Test
- **ST:** System Test (E2E)
- **PT:** Performance Test
- **UAT:** User Acceptance Test
- **DOC:** Documentation Review
- **CR:** Code Review
