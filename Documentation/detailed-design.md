# Detailed Design

**Version 1.0**

**Date:** 2026-01-02

---

## 1. Introduction

This document provides the detailed design for the Core Logic and Infrastructure layers of the Project Dashboard. It defines the specific classes, interfaces, methods, and data structures that will be implemented. The design is presented in a language-agnostic, TypeScript-like syntax.

## 2. Domain Models

These are the core data structures of the application. They are plain objects with no business logic.

```typescript
// Represents a single executable command
interface Target {
    id: string;          // Unique identifier (e.g., UUID)
    name: string;        // Display name (e.g., "build")
    command: string;     // The actual command to execute
    sourceFile: string;  // Path to the file this target came from (e.g., "Makefile")
    notes?: string;      // User-added description
    groupId?: string;    // ID of the group this target belongs to
}

// Represents a user-defined group of targets
interface TargetGroup {
    id: string;
    name: string;
    displayOrder: number;
}

// Represents the entire project configuration, to be serialized/deserialized
interface ProjectConfig {
    version: string;
    projectName: string;
    targets: Target[];
    groups: TargetGroup[];
    shell?: string; // The shell to use for execution on this project
}
```

## 3. Infrastructure Layer Interfaces

These interfaces define the contract that the Infrastructure Layer must fulfill. The Core Logic layer will code against these interfaces, not the concrete implementations.

```typescript
// Interface for file system operations
interface IFileSystemAdapter {
    fileExists(path: string): Promise<boolean>;
    readFile(path: string): Promise<string>;
    writeFile(path: string, content: string): Promise<void>;
    findFiles(pattern: string, rootDir: string): Promise<string[]>; // e.g., find all "Makefile"
}

// Represents a running process
interface IRunningProcess {
    pid: number;
    on(event: 'data', listener: (chunk: string) => void): void;
    on(event: 'error', listener: (error: Error) => void): void;
    on(event: 'close', listener: (code: number) => void): void;
    kill(): void;
}

// Interface for shell command execution
interface IShellAdapter {
    execute(command: string, workingDir: string, shell: string): IRunningProcess;
    getSystemShell(): string; // Detects the default system shell
}
```

## 4. Core Logic Layer Design

### 4.1. ConfigurationService

- **Responsibility:** Manages the loading and saving of the `ProjectConfig`.
- **Dependencies:** `IFileSystemAdapter`, `ConfigSerializer/Parser` (from Infrastructure)

```typescript
class ConfigurationService {
    constructor(
        private fsAdapter: IFileSystemAdapter,
        private serializer: IConfigSerializer // Assume a serializer/parser interface
    );

    async loadConfig(projectRoot: string): Promise<ProjectConfig | null>;
    async saveConfig(projectRoot: string, config: ProjectConfig): Promise<void>;
}
```

### 4.2. DiscoveryService

- **Responsibility:** Scans for and parses potential targets.
- **Dependencies:** `IFileSystemAdapter`

```typescript
class DiscoveryService {
    constructor(private fsAdapter: IFileSystemAdapter);

    async discoverTargets(projectRoot: string): Promise<Target[]>;
    private async discoverFromMakefiles(projectRoot: string): Promise<Target[]>;
    private async discoverFromPackageJson(projectRoot: string): Promise<Target[]>;
    private async discoverFromScripts(projectRoot: string): Promise<Target[]>;
}
```

### 4.3. ExecutionService

- **Responsibility:** Manages the execution of targets.
- **Dependencies:** `IShellAdapter`

```typescript
class ExecutionService {
    constructor(private shellAdapter: IShellAdapter);

    // Returns the process ID of the spawned process
    runTarget(target: Target, projectRoot: string, shell: string): number;
    cancelTarget(pid: number): void;
    getRunningProcesses(): number[];
}
```

### 4.4. ProjectService (Facade)

- **Responsibility:** Acts as the primary entry point for the UI layer, orchestrating the other services.
- **Dependencies:** `ConfigurationService`, `DiscoveryService`, `ExecutionService`

```typescript
class ProjectService {
    constructor(
        private configService: ConfigurationService,
        private discoveryService: DiscoveryService,
        private executionService: ExecutionService
    );

    async loadProject(projectRoot: string): Promise<ProjectConfig>;
    async runTarget(targetId: string): Promise<void>;
    async cancelTarget(pid: number): Promise<void>;
    // ... other methods for adding/editing/grouping targets
}
```
