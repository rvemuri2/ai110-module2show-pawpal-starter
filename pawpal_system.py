"""
PawPal+ core classes, implemented from the UML class diagram.

Classes: Owner, Pet, Task, Scheduler (Priority is a supporting enum).
"""

from enum import Enum
from typing import List, Optional
from datetime import datetime, timedelta


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
        """Create a task representing one pet care activity."""
        self.id = id
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.is_flexible = is_flexible
        self.completed = completed

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


class Pet:
    def __init__(self, name: str, species: str, owner: Optional["Owner"] = None):
        """Create a pet, optionally linked to an owner."""
        self.name = name
        self.species = species
        self.owner = owner  # back-reference so Scheduler can reach preferences
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks associated with this pet."""
        return self.tasks


class Owner:
    def __init__(self, name: str, preferences: Optional[dict] = None):
        """Create an owner with an optional preferences dict."""
        self.name = name
        self.preferences = preferences or {}
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets, and set pet.owner back-reference."""
        pet.owner = self
        self.pets.append(pet)

    def set_preference(self, key: str, value) -> None:
        """Set or update an owner preference (e.g. preferred walk time)."""
        self.preferences[key] = value


class Scheduler:
    """
    Stateless by design: available_minutes and preferences are passed into
    generate_plan() per call, rather than stored on the instance. This avoids
    the ambiguity of a Scheduler holding a stale budget across multiple plans.

    Scheduling rules (in order of precedence):
    1. Completed tasks are dropped before anything else, they don't need a slot.
    2. Fixed-time tasks (is_flexible=False) are placed first, since they
       represent commitments that can't move (e.g. meds at a specific time).
    3. Remaining flexible tasks are sorted by priority (HIGH > MEDIUM > LOW).
    4. Ties within the same priority are broken by shorter duration first,
       so quick wins get scheduled before time runs out.
    5. Tasks are added greedily until they no longer fit in the remaining
       time budget; anything left over goes into "unscheduled".
    """

    _PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

    def generate_plan(
        self,
        tasks: List[Task],
        available_minutes: int,
        preferences: Optional[dict] = None,
        start_time: str = "08:00",
    ) -> dict:
        """Build a daily plan by filtering, ordering, and time-slotting tasks within the time budget."""
        preferences = preferences or {}

        # Rule 1: drop already-completed tasks, they don't need scheduling.
        active_tasks = [t for t in tasks if not t.completed]

        # Rule 2: fixed-time tasks go first, in the order given.
        fixed_tasks = [t for t in active_tasks if not t.is_flexible]
        flexible_tasks = [t for t in active_tasks if t.is_flexible]

        # Rule 3 + 4: sort flexible tasks by priority, then duration.
        sorted_flexible = self._sort_by_priority(flexible_tasks)

        ordered_candidates = fixed_tasks + sorted_flexible

        scheduled: List[Task] = []
        unscheduled: List[Task] = []
        timeline: List[dict] = []
        remaining = available_minutes

        current_time = datetime.strptime(start_time, "%H:%M")

        # Rule 5: greedily fill the schedule, assigning real time slots.
        for task in ordered_candidates:
            if self._fits_in_remaining_time(task, remaining):
                task_start = current_time
                task_end = current_time + timedelta(minutes=task.duration_minutes)

                scheduled.append(task)
                timeline.append(
                    {
                        "task": task,
                        "start": task_start.strftime("%I:%M %p"),
                        "end": task_end.strftime("%I:%M %p"),
                    }
                )

                current_time = task_end
                remaining -= task.duration_minutes
            else:
                unscheduled.append(task)

        total_minutes_used = available_minutes - remaining

        reasoning = self.explain_plan(timeline, unscheduled)

        return {
            "scheduled": scheduled,
            "timeline": timeline,
            "unscheduled": unscheduled,
            "total_minutes_used": total_minutes_used,
            "reasoning": reasoning,
        }

    def explain_plan(self, timeline: List[dict], skipped: List[Task]) -> str:
        """Return a human-readable explanation of why the plan looks this way."""
        if not timeline and not skipped:
            return "No tasks were provided, so there's nothing to schedule."

        lines = []

        if timeline:
            lines.append("Scheduled tasks (in order):")
            for entry in timeline:
                task = entry["task"]
                reason_bits = [f"{task.priority.value} priority"]
                if not task.is_flexible:
                    reason_bits.append("fixed-time commitment")
                lines.append(
                    f"  - {entry['start']} - {entry['end']}: {task.title} "
                    f"({task.duration_minutes} min), included because it's "
                    f"{' and '.join(reason_bits)}."
                )
        else:
            lines.append("No tasks were scheduled with the available time.")

        if skipped:
            lines.append("Unscheduled tasks:")
            for task in skipped:
                lines.append(
                    f"  - {task.title} ({task.duration_minutes} min): "
                    f"skipped because there wasn't enough remaining time "
                    f"after higher-priority or fixed-time tasks were placed."
                )

        return "\n".join(lines)

    def _sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (HIGH first), breaking ties by shorter duration."""
        return sorted(
            tasks,
            key=lambda t: (self._PRIORITY_ORDER[t.priority], t.duration_minutes),
        )

    def _fits_in_remaining_time(self, task: Task, remaining: int) -> bool:
        """Check whether a task fits in the remaining time budget."""
        return task.duration_minutes <= remaining