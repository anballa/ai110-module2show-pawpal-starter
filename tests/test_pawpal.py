import pytest
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


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


def test_scheduler_sort_by_time_chronological():
    owner = Owner(name='Alex', contact='alex@example.com')
    pet = Pet(name='Milo', type='dog', age=4, breed='beagle')
    owner.add_pet(pet)

    now = datetime.now().replace(second=0, microsecond=0)
    task_a = Task(id='a', title='First', duration=10, priority=1, start=now + timedelta(hours=3), end=now + timedelta(hours=3, minutes=10), assigned_pet=pet)
    task_b = Task(id='b', title='Second', duration=10, priority=1, start=now + timedelta(hours=1), end=now + timedelta(hours=1, minutes=10), assigned_pet=pet)
    task_c = Task(id='c', title='Third', duration=10, priority=1, start=now + timedelta(hours=2), end=now + timedelta(hours=2, minutes=10), assigned_pet=pet)

    pet.add_task(task_a)
    pet.add_task(task_b)
    pet.add_task(task_c)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()

    assert [t.id for t in sorted_tasks] == ['b', 'c', 'a']


def test_recurring_daily_task_creates_next_occurrence():
    owner = Owner(name='Alex', contact='alex@example.com')
    pet = Pet(name='Milo', type='dog', age=4, breed='beagle')
    owner.add_pet(pet)

    now = datetime.now().replace(second=0, microsecond=0)
    task = Task(id='daily1', title='Daily Walk', duration=30, priority=5, start=now, end=now + timedelta(minutes=30), assigned_pet=pet, repeat_interval='daily')
    pet.add_task(task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete('daily1')

    assert task.completed is True
    assert next_task is not None
    assert next_task.assigned_pet == pet
    assert next_task.repeat_interval == 'daily'
    assert next_task.start.date() == (now + timedelta(days=1)).date()


def test_inspect_conflicts_flags_overlap():
    owner = Owner(name='Alex', contact='alex@example.com')
    pet = Pet(name='Luna', type='cat', age=2, breed='shorthair')
    owner.add_pet(pet)

    now = datetime.now().replace(second=0, microsecond=0)
    t1 = Task(id='t1', title='Feed', duration=20, priority=5, start=now, end=now + timedelta(minutes=20), assigned_pet=pet)
    t2 = Task(id='t2', title='Vet', duration=20, priority=5, start=now + timedelta(minutes=10), end=now + timedelta(minutes=30), assigned_pet=pet)
    pet.add_task(t1)
    pet.add_task(t2)

    scheduler = Scheduler(owner)
    warnings = scheduler.inspect_conflicts()

    assert len(warnings) >= 1
    assert 'overlaps with' in warnings[0]


def test_empty_pet_schedule_no_conflicts():
    owner = Owner(name='Alex', contact='alex@example.com')
    pet = Pet(name='Luna', type='cat', age=2, breed='shorthair')
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    warnings = scheduler.inspect_conflicts()

    assert len(warnings) == 0


def test_empty_pet_schedule_generates_empty_plan():
    owner = Owner(name='Alex', contact='alex@example.com')
    pet = Pet(name='Luna', type='cat', age=2, breed='shorthair')
    owner.add_pet(pet)

    now = datetime.now().replace(second=0, microsecond=0)
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(now)

    assert len(plan.tasks) == 0
    assert plan.explanation == f"Generated 0 tasks for {now.date()} sorted by time and priority."


