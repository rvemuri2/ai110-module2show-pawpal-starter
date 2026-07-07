"""
PawPal+ core classes, implemented from the UML class diagram.

Classes: Owner, Pet, Task, Scheduler (Priority is a supporting enum).
"""

from enum import Enum
from typing import List, Optional
from datetime import datetime, timedelta, date


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
        fixed_time: Optional[str] = None,
        frequency: Optional[str] = None,
        due_date: Optional[date] = None,
    ):
        """Create a task representing one pet care activity."""
        self.id = id
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.is_flexible = is_flexible
        self.completed = completed
        self.fixed_time = fixed_time  # "HH:MM" anchor time for non-flexible tasks
        self.frequency = frequency  # None, "daily", or "weekly"
        self.due_date = due_date or (date.today() if frequency else None)
        self.last_completed_date: Optional[date] = None
        self.pet: Optional["Pet"] = None  # back-reference, set by Pet.add_task()

    def mark_complete(self, completed_date: Optional[date] = None) -> Optional["Task"]:
        """
        Mark this task as completed. If it's a "daily" or "weekly" task, this
        also creates and returns the next occurrence, automatically added to
        the same pet's task list (if this task is attached to a pet).
        """
        self.completed = True
        self.last_completed_date = completed_date or date.today()

        if self.frequency in ("daily", "weekly"):
            next_task = self._create_next_occurrence(self.last_completed_date)
            if self.pet is not None:
                self.pet.add_task(next_task)
            return next_task

        return None

    def _create_next_occurrence(self, from_date: date) -> "Task":
        """Build the next occurrence of a recurring task, due after the correct interval."""
        if self.frequency == "daily":
            next_due = from_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = from_date + timedelta(weeks=1)
        else:
            next_due = from_date

        return Task(
            id=f"{self.id}-{next_due.isoformat()}",
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            is_flexible=self.is_flexible,
            completed=False,
            fixed_time=self.fixed_time,
            frequency=self.frequency,
            due_date=next_due,
        )

    def is_due(self, today: Optional[date] = None) -> bool:
        """Return True if this task has no due date, or its due date has arrived."""
        if self.due_date is None:
            return True
        today = today or date.today()
        return self.due_date <= today


class Pet:
    def __init__(self, name: str, species: str, owner: Optional["Owner"] = None):
        """Create a pet, optionally linked to an owner."""
        self.name = name
        self.species = species
        self.owner = owner  # back-reference so Scheduler can reach preferences
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        task.pet = self
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks associated with this pet."""
        return self.tasks

    def get_tasks_by_status(self, completed: bool) -> List[Task]:
        """Return this pet's tasks filtered by completion status."""
        return [t for t in self.tasks if t.completed == completed]

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """
        Mark one of this pet's tasks complete. Delegates to Task.mark_complete(),
        which handles spawning the next occurrence for daily/weekly tasks and
        adding it back onto this pet's task list.
        """
        return task.mark_complete()


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

    def get_tasks(
        self,
        pet_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Task]:
        """Return tasks across all pets, optionally filtered by pet name and/or status."""
        pets = self.pets if pet_name is None else [p for p in self.pets if p.name == pet_name]

        tasks: List[Task] = []
        for pet in pets:
            tasks.extend(pet.get_tasks())

        if status == "completed":
            tasks = [t for t in tasks if t.completed]
        elif status == "pending":
            tasks = [t for t in tasks if not t.completed]

        return tasks


def _time_to_minutes(hhmm: str) -> int:
    """Convert an "HH:MM" string into minutes since midnight, for time comparisons."""
    hours, minutes = map(int, hhmm.split(":"))
    return hours * 60 + minutes


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
    6. Fixed-time tasks with an explicit fixed_time are anchored to that
       clock time rather than just stacked wherever the pointer currently is.
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

        # Flag overlapping fixed-time tasks up front, before scheduling even runs,
        # so the owner can see the problem instead of it being silently masked.
        conflicts = self.detect_conflicts(active_tasks)

        # Rule 2: fixed-time tasks go first, ordered by their anchor time if set.
        fixed_tasks = self.sort_by_time(
            [t for t in active_tasks if not t.is_flexible]
        )
        flexible_tasks = [t for t in active_tasks if t.is_flexible]

        # Rule 3 + 4: sort flexible tasks by priority, then duration.
        sorted_flexible = self._sort_by_priority(flexible_tasks)

        ordered_candidates = fixed_tasks + sorted_flexible

        scheduled: List[Task] = []
        unscheduled: List[Task] = []
        timeline: List[dict] = []
        remaining = available_minutes

        current_time = datetime.strptime(start_time, "%H:%M")

        # Rule 5 + 6: greedily fill the schedule, honoring fixed_time anchors.
        for task in ordered_candidates:
            if self._fits_in_remaining_time(task, remaining):
                if task.fixed_time:
                    anchor = datetime.strptime(task.fixed_time, "%H:%M")
                    task_start = max(anchor, current_time)
                else:
                    task_start = current_time

                task_end = task_start + timedelta(minutes=task.duration_minutes)

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

        reasoning = self.explain_plan(timeline, unscheduled, conflicts)

        return {
            "scheduled": scheduled,
            "timeline": timeline,
            "unscheduled": unscheduled,
            "conflicts": conflicts,
            "total_minutes_used": total_minutes_used,
            "reasoning": reasoning,
        }

    def explain_plan(
        self,
        timeline: List[dict],
        skipped: List[Task],
        conflicts: Optional[List[tuple]] = None,
    ) -> str:
        """Return a human-readable explanation of why the plan looks this way."""
        conflicts = conflicts or []

        if not timeline and not skipped:
            return "No tasks were provided, so there's nothing to schedule."

        lines = []

        if conflicts:
            lines.append("Scheduling conflicts detected:")
            for task_a, task_b in conflicts:
                lines.append(
                    f"  - '{task_a.title}' ({task_a.fixed_time}) overlaps with "
                    f"'{task_b.title}' ({task_b.fixed_time}). Consider adjusting one of these times."
                )
            lines.append("")

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

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks chronologically by their fixed_time "HH:MM" string; tasks with no fixed_time sort last."""
        # "HH:MM" is zero-padded (e.g. "08:00", "18:00"), so plain string comparison
        # already sorts correctly, no need to convert to minutes first.
        return sorted(
            tasks,
            key=lambda t: (t.fixed_time is None, t.fixed_time or ""),
        )

    def filter_tasks(
        self,
        tasks: List[Task],
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Filter a list of tasks by completion status and/or the name of the pet they belong to."""
        result = tasks

        if completed is not None:
            result = [t for t in result if t.completed == completed]

        if pet_name is not None:
            result = [t for t in result if t.pet is not None and t.pet.name == pet_name]

        return result

    def detect_conflicts(self, tasks: List[Task]) -> List[tuple]:
        """
        Find pairs of fixed-time tasks whose time windows overlap, regardless
        of whether they belong to the same pet or different pets. Only tasks
        with a fixed_time set are checked; flexible tasks can't conflict since
        they have no anchored clock time.

        Uses a sweep: sort tasks by start time, then walk through once,
        comparing each task only against others still "active" (not yet
        ended). This mirrors how a person would actually scan a schedule for
        overlaps, rather than blindly comparing every pair against every other.
        """
        fixed = sorted(
            (t for t in tasks if t.fixed_time),
            key=lambda t: _time_to_minutes(t.fixed_time),
        )

        conflicts = []
        active: List[Task] = []  # tasks whose time window hasn't ended yet

        for task in fixed:
            start = _time_to_minutes(task.fixed_time)

            # Drop anything from `active` that already ended before this one starts.
            active = [
                a for a in active
                if _time_to_minutes(a.fixed_time) + a.duration_minutes > start
            ]

            # Everything still active at this point genuinely overlaps `task`.
            for other in active:
                conflicts.append((other, task))

            active.append(task)

        return conflicts

    def check_for_conflicts(self, tasks: List[Task]) -> str:
        """
        Lightweight conflict check: returns a human-readable warning string
        describing any overlaps, or an empty string if there are none. Never
        raises, even on malformed task data, so a bad fixed_time value can't
        crash the whole scheduling flow, it just gets skipped and reported.
        """
        try:
            conflicts = self.detect_conflicts(tasks)
        except (ValueError, AttributeError) as error:
            return f"⚠️ Could not fully check for conflicts due to bad task data: {error}"

        if not conflicts:
            return ""

        lines = ["⚠️ Scheduling conflicts detected:"]
        for task_a, task_b in conflicts:
            pet_a = task_a.pet.name if task_a.pet else "an unassigned pet"
            pet_b = task_b.pet.name if task_b.pet else "an unassigned pet"

            if task_a.pet is task_b.pet:
                lines.append(
                    f"  - {pet_a}: '{task_a.title}' ({task_a.fixed_time}) overlaps "
                    f"with '{task_b.title}' ({task_b.fixed_time})."
                )
            else:
                lines.append(
                    f"  - '{task_a.title}' for {pet_a} ({task_a.fixed_time}) overlaps "
                    f"with '{task_b.title}' for {pet_b} ({task_b.fixed_time})."
                )

        return "\n".join(lines)