"""
tests/test_pawpal.py

Simple unit tests for the PawPal+ core classes.
"""

import sys
import os

# Allow importing pawpal_system.py from the parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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