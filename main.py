from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner and pets
owner = Owner(name="Alex", contact="alex@example.com", availability=["morning", "afternoon"])
pet1 = Pet(name="Milo", type="dog", age=4, breed="beagle")
pet2 = Pet(name="Luna", type="cat", age=2, breed="shorthair")
owner.add_pet(pet1)
owner.add_pet(pet2)

# Create tasks (out of order intentionally)
now = datetime.now().replace(second=0, microsecond=0)
med_task = Task(
    id="t3",
    title="Medication",
    duration=5,
    priority=8,
    start=now + timedelta(hours=1, minutes=45),
    end=now + timedelta(hours=1, minutes=50),
    assigned_pet=pet2,
)

walk_task = Task(
    id="t1",
    title="Morning walk",
    duration=30,
    priority=10,
    start=now + timedelta(hours=1),
    end=now + timedelta(hours=1, minutes=30),
    assigned_pet=pet1,
    repeat_interval="daily",
)

feed_task = Task(
    id="t2",
    title="Breakfast",
    duration=10,
    priority=9,
    start=now + timedelta(hours=2),
    end=now + timedelta(hours=2, minutes=10),
    assigned_pet=pet1,
)

conflict_task = Task(
    id="t4",
    title="Conflict check walk",
    duration=20,
    priority=7,
    start=now + timedelta(hours=1, minutes=15),
    end=now + timedelta(hours=1, minutes=35),
    assigned_pet=pet1,
)

pet2.add_task(med_task)
pet1.add_task(feed_task)
pet1.add_task(conflict_task)
pet1.add_task(walk_task)

# Scheduler
scheduler = Scheduler(owner)

print("\n--- Initial tasks (unsorted load order) ---")
for t in owner.get_all_tasks():
    print(f"* {t.id}: {t.title} @ {t.start.strftime('%H:%M')} pet={t.assigned_pet.name} completed={t.completed}")

sorted_tasks = scheduler.sort_by_time()
print("\n--- Sorted tasks by time ---")
for t in sorted_tasks:
    print(f"* {t.id}: {t.title} @ {t.start.strftime('%H:%M')} pet={t.assigned_pet.name}")

filtered_by_milo = scheduler.filter_tasks(pet_name="Milo", completed=False)
print("\n--- Filtered tasks for Milo, pending ---")
for t in filtered_by_milo:
    print(f"* {t.id}: {t.title} @ {t.start.strftime('%H:%M')}")

# Mark a recurring task complete and check automation
next_occurrence = scheduler.mark_task_complete("t1")
print("\n--- Marked t1 complete (recurring daily) ---")
print(f"next_occurrence: {next_occurrence.id if next_occurrence else None} at {next_occurrence.start.strftime('%Y-%m-%d %H:%M') if next_occurrence else 'N/A'}")

# Conflict detection
conflict_warnings = scheduler.inspect_conflicts()
print("\n--- Conflict Warnings ---")
if conflict_warnings:
    for note in conflict_warnings:
        print(note)
else:
    print("No conflicts detected.")

# Daily plan for today
plan = scheduler.generate_daily_plan(now)
print("\n--- Today's Schedule (generated) ---")
for task in plan.tasks:
    pet_name = task.assigned_pet.name if task.assigned_pet else "Unknown"
    start_str = task.start.strftime('%H:%M') if task.start else "TBD"
    end_str = task.end.strftime('%H:%M') if task.end else "TBD"
    print(f"- {start_str} to {end_str}: {task.title} for {pet_name} (priority {task.priority})")

print("\nExplanation:", plan.explanation)

