"""
PawPal+ class skeleton, generated from the UML class diagram.

This file only defines structure (attributes + method signatures).
No scheduling logic is implemented yet, that comes in the next step.
"""

from enum import Enum
from typing import List, Optional


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task:
    def __init__(
        self,
        id: str,
        title: str,
        duration_minutes: int,
        priority: Priority,
        category: str,
        is_flexible: bool = True,
        completed: bool = False,
    ):
        self.id = id
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.is_flexible = is_flexible
        self.completed = completed


class Pet:
    def __init__(self, name: str, species: str, owner: Optional["Owner"] = None):
        self.name = name
        self.species = species
        self.owner = owner  # back-reference so Scheduler can reach preferences
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        pass

    def get_tasks(self) -> List[Task]:
        """Return all tasks associated with this pet."""
        pass


class Owner:
    def __init__(self, name: str, preferences: Optional[dict] = None):
        self.name = name
        self.preferences = preferences or {}
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets, and set pet.owner back-reference."""
        pass

    def set_preference(self, key: str, value) -> None:
        """Set or update an owner preference (e.g. preferred walk time)."""
        pass


class Scheduler:
    """
    Stateless by design: available_minutes and preferences are passed into
    generate_plan() per call, rather than stored on the instance. This avoids
    the ambiguity of a Scheduler holding a stale budget across multiple plans.
    """

    def generate_plan(
        self,
        tasks: List[Task],
        available_minutes: int,
        preferences: Optional[dict] = None,
    ) -> dict:
        """
        Build a daily plan from the given tasks and time budget.

        Returns a dict, e.g.:
        {
            "scheduled": [...],
            "unscheduled": [...],
            "total_minutes_used": int,
        }
        """
        pass

    def explain_plan(self, scheduled: List[Task], skipped: List[Task]) -> str:
        """Return a human-readable explanation of why the plan looks this way."""
        pass

    def _sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (private helper)."""
        pass

    def _fits_in_remaining_time(self, task: Task, remaining: int) -> bool:
        """Check whether a task fits in the remaining time budget (private helper)."""
        pass