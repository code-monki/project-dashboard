"""
This module defines the core data models for the Project Dashboard application,
as specified in the Detailed Design document. These models are plain data
structures with no business logic.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import uuid

@dataclass
class Target:
    """Represents a single executable command."""
    name: str
    command: str
    source_file: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    notes: Optional[str] = None
    group_id: Optional[str] = None


@dataclass
class TargetGroup:
    """Represents a user-defined group of targets."""
    name: str
    display_order: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ProjectConfig:
    """Represents the entire project configuration, to be serialized."""
    project_name: str
    targets: List[Target] = field(default_factory=list)
    groups: List[TargetGroup] = field(default_factory=list)
    version: str = "1.0"
    shell: Optional[str] = None
