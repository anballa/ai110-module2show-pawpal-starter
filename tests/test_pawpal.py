import pytest
from datetime import datetime, timedelta
from pawpal_system import Pet, Task


def test_task_completion_marks_completed():
    task = Task(id="t1", title="Feed", duration=15, priority=5)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_pet_add_task_increases_task_count():
    pet = Pet(name="Milo", type="dog", age=4, breed="beagle")
    initial_count = len(pet.tasks)

    task = Task(id="t2", title="Walk", duration=30, priority=10)
    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1
    assert pet.tasks[-1] == task
