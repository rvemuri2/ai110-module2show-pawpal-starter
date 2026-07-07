"""
tests/test_pawpal.py

Simple unit tests for the PawPal+ core classes.
"""

import sys
import os

# Allow importing pawpal_system.py from the parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta

from pawpal_system import Task, Pet, Priority


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