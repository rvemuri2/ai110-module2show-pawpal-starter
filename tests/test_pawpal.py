"""
tests/test_pawpal.py

Simple unit tests for the PawPal+ core classes.
"""

import sys
import os

# Allow importing pawpal_system.py from the parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta

from pawpal_system import Task, Pet, Priority, Scheduler


def test_task_completion():
    """Verify that calling mark_complete() actually changes the task's status."""
    task = Task(
        id="1",
        title="Morning walk",
        duration_minutes=20,
        priority=Priority.HIGH,
        category="exercise",
    )

    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition_increases_pet_task_count():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet(name="Mochi", species="dog")

    assert len(pet.get_tasks()) == 0

    task = Task(
        id="1",
        title="Morning walk",
        duration_minutes=20,
        priority=Priority.HIGH,
        category="exercise",
    )
    pet.add_task(task)

    assert len(pet.get_tasks()) == 1


def test_daily_task_spawns_next_occurrence_due_tomorrow():
    """Verify completing a daily task creates a new pending task due tomorrow."""
    pet = Pet(name="Mochi", species="dog")
    task = Task(
        id="1",
        title="Give meds",
        duration_minutes=5,
        priority=Priority.HIGH,
        category="health",
        frequency="daily",
    )
    pet.add_task(task)

    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task in pet.get_tasks()
    assert len(pet.get_tasks()) == 2


def test_non_recurring_task_does_not_spawn_next_occurrence():
    """Verify a one-off task (no frequency) does not create a new task on completion."""
    pet = Pet(name="Mochi", species="dog")
    task = Task(
        id="1",
        title="Vet visit",
        duration_minutes=30,
        priority=Priority.HIGH,
        category="health",
    )
    pet.add_task(task)

    result = task.mark_complete()

    assert result is None
    assert len(pet.get_tasks()) == 1


def test_weekly_task_spawns_next_occurrence_due_in_seven_days():
    """Verify completing a weekly task creates a new pending task due exactly 7 days later."""
    pet = Pet(name="Luna", species="cat")
    task = Task(
        id="1",
        title="Grooming",
        duration_minutes=30,
        priority=Priority.MEDIUM,
        category="grooming",
        frequency="weekly",
    )
    pet.add_task(task)

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(weeks=1)
    assert len(pet.get_tasks()) == 2


def test_recurring_task_without_a_pet_does_not_crash():
    """Verify mark_complete() on a recurring task with no pet attached still works."""
    task = Task(
        id="1",
        title="Give meds",
        duration_minutes=5,
        priority=Priority.HIGH,
        category="health",
        frequency="daily",
    )
    # Note: never added to a Pet, so task.pet is None.

    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_sort_by_time_returns_chronological_order():
    """Verify sort_by_time() returns fixed-time tasks in chronological order, regardless of input order."""
    scheduler = Scheduler()

    evening = Task("1", "Evening walk", 20, Priority.HIGH, "exercise", is_flexible=False, fixed_time="18:00")
    morning = Task("2", "Give meds", 5, Priority.HIGH, "health", is_flexible=False, fixed_time="08:00")
    midday = Task("3", "Midday check-in", 5, Priority.LOW, "enrichment", is_flexible=False, fixed_time="12:30")

    # Added deliberately out of order.
    sorted_tasks = scheduler.sort_by_time([evening, morning, midday])

    assert [t.title for t in sorted_tasks] == ["Give meds", "Midday check-in", "Evening walk"]


def test_sort_by_time_puts_flexible_tasks_last():
    """Verify tasks with no fixed_time sort after all fixed-time tasks."""
    scheduler = Scheduler()

    flexible = Task("1", "Play fetch", 15, Priority.MEDIUM, "enrichment")  # no fixed_time
    fixed = Task("2", "Give meds", 5, Priority.HIGH, "health", is_flexible=False, fixed_time="08:00")

    sorted_tasks = scheduler.sort_by_time([flexible, fixed])

    assert sorted_tasks[0].title == "Give meds"
    assert sorted_tasks[1].title == "Play fetch"


def test_detect_conflicts_flags_duplicate_times():
    """Verify the Scheduler flags two tasks scheduled at the exact same time."""
    scheduler = Scheduler()

    task_a = Task("1", "Nail trim", 15, Priority.LOW, "grooming", is_flexible=False, fixed_time="10:00")
    task_b = Task("2", "Training session", 20, Priority.MEDIUM, "enrichment", is_flexible=False, fixed_time="10:00")

    conflicts = scheduler.detect_conflicts([task_a, task_b])

    assert len(conflicts) == 1
    assert task_a in conflicts[0]
    assert task_b in conflicts[0]


def test_detect_conflicts_ignores_back_to_back_tasks():
    """Verify tasks that end exactly when another starts are NOT flagged as conflicts."""
    scheduler = Scheduler()

    task_a = Task("1", "Task A", 30, Priority.MEDIUM, "general", is_flexible=False, fixed_time="09:00")  # 09:00-09:30
    task_b = Task("2", "Task B", 30, Priority.MEDIUM, "general", is_flexible=False, fixed_time="09:30")  # 09:30-10:00

    conflicts = scheduler.detect_conflicts([task_a, task_b])

    assert conflicts == []


def test_check_for_conflicts_returns_empty_string_when_no_conflicts():
    """Verify check_for_conflicts() returns an empty string, not None, when nothing overlaps."""
    scheduler = Scheduler()

    task = Task("1", "Play", 10, Priority.LOW, "enrichment", is_flexible=False, fixed_time="14:00")

    result = scheduler.check_for_conflicts([task])

    assert result == ""


def test_generate_plan_with_no_tasks_does_not_crash():
    """Verify generate_plan() handles an empty task list gracefully."""
    scheduler = Scheduler()

    plan = scheduler.generate_plan(tasks=[], available_minutes=45)

    assert plan["scheduled"] == []
    assert plan["unscheduled"] == []
    assert plan["total_minutes_used"] == 0
    assert "nothing to schedule" in plan["reasoning"]


def test_generate_plan_skips_task_that_does_not_fit_budget():
    """Verify a task longer than the entire time budget lands in 'unscheduled', not scheduled or crashed."""
    scheduler = Scheduler()

    oversized_task = Task("1", "Long grooming session", 60, Priority.MEDIUM, "grooming")

    plan = scheduler.generate_plan(tasks=[oversized_task], available_minutes=30)

    assert oversized_task not in plan["scheduled"]
    assert oversized_task in plan["unscheduled"]
    assert plan["total_minutes_used"] == 0