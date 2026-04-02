from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional


@dataclass
class Task:
    id: str
    title: str
    duration: int
    priority: int
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    assigned_pet: Optional["Pet"] = None
    completed: bool = False
    repeat_interval: Optional[str] = None

    def reschedule(self, start: datetime, end: Optional[datetime] = None):
        """Reschedule the task start/end times."""
        self.start = start
        self.end = end or start + timedelta(minutes=self.duration)

    def update_priority(self, level: int):
        """Adjust task priority."""
        self.priority = level

    def mark_complete(self):
        """Mark this task as complete and return a next occurrence if repeating."""
        self.completed = True
        return self.create_next_occurrence()

    def create_next_occurrence(self):
        """Return a newly scheduled Task for repeat_interval daily/weekly."""
        if not self.repeat_interval or not self.start:
            return None

        if self.repeat_interval == "daily":
            delta = timedelta(days=1)
        elif self.repeat_interval == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None

        new_start = self.start + delta
        new_end = self.end + delta if self.end else new_start + timedelta(minutes=self.duration)

        # Keep ID unique by appending new date
        new_id = f"{self.id}_{new_start.date()}"

        next_task = Task(
            id=new_id,
            title=self.title,
            duration=self.duration,
            priority=self.priority,
            start=new_start,
            end=new_end,
            assigned_pet=self.assigned_pet,
            completed=False,
            repeat_interval=self.repeat_interval,
        )

        return next_task

    def is_due(self, date: datetime) -> bool:
        """Return true if task is due on the given date."""
        if self.completed:
            return False
        if self.start:
            return self.start.date() == date.date()
        return True


@dataclass
class Pet:
    name: str
    type: str
    age: int
    breed: str
    special_needs: Optional[str] = None
    owner_ref: Optional["Owner"] = None
    tasks: List[Task] = field(default_factory=list)

    def update_profile(self, **kwargs):
        """Update pet profile fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def needs_medication_now(self, at_time: datetime) -> bool:
        """Check if medication task is due now for this pet."""
        for task in self.tasks:
            if task.title.lower() in ("medication", "meds", "medicine") and not task.completed:
                if task.start and task.start.date() == at_time.date():
                    return True
        return False

    def describe(self) -> str:
        """Return a human-readable pet description."""
        return f"{self.name} the {self.breed} ({self.type}), {self.age} years old." \
               f" Special needs: {self.special_needs or 'none'}."

    def add_task(self, task: Task):
        """Assign a task to this pet."""
        task.assigned_pet = self
        self.tasks.append(task)

    def remove_task(self, task_id: str):
        """Remove a task by ID from this pet."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks(self) -> List[Task]:
        """Get tasks assigned to this pet."""
        return self.tasks


@dataclass
class Owner:
    name: str
    contact: str
    availability: List[str] = field(default_factory=list)
    preferences: Dict[str, str] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Attach a pet to this owner."""
        pet.owner_ref = self
        self.pets.append(pet)

    def update_availability(self, availability: List[str]):
        """Update the owner's available time slots."""
        self.availability = availability

    def update_preferences(self, preferences: Dict[str, str]):
        """Set owner care preferences."""
        self.preferences = preferences

    def is_available(self, time_slot: str) -> bool:
        """Check if owner is available for a timeslot."""
        return time_slot in self.availability

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks across all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks


@dataclass
class Schedule:
    date: datetime
    tasks: List[Task] = field(default_factory=list)
    explanation: Optional[str] = None


class Scheduler:
    def __init__(self, owner: Owner, pets: Optional[List[Pet]] = None, constraints: Optional[Dict] = None):
        self.owner = owner
        self.pets = pets or owner.pets
        self.constraints = constraints or {}

    def all_tasks(self) -> List[Task]:
        """Get all tasks from owner pets."""
        return self.owner.get_all_tasks()

    def pending_tasks(self) -> List[Task]:
        """Get tasks that are not completed."""
        return [t for t in self.all_tasks() if not t.completed]

    def mark_task_complete(self, task_id: str) -> Optional[Task]:
        """Mark a task as complete; schedule repeat task if repeating."""
        for task in self.all_tasks():
            if task.id == task_id:
                next_task = task.mark_complete()
                if next_task and task.assigned_pet:
                    task.assigned_pet.add_task(next_task)
                return next_task
        return None

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by start time, with non-start tasks at the end.

        Inline Chat: How can we use Python's sorted() with key=lambda to sort HH:MM strings?
        Ans: sorted(time_strings, key=lambda x: datetime.strptime(x, '%H:%M'))
        """
        tasks = tasks if tasks is not None else self.all_tasks()

        def parse_time_key(task):
            if task.start:
                return task.start
            # unspecified time tasks go last
            return datetime.max

        return sorted(tasks, key=parse_time_key)

    def filter_tasks(self, pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
        """Filter tasks by pet name and/or completion status."""
        tasks = self.all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.assigned_pet and t.assigned_pet.name.lower() == pet_name.lower()]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def generate_daily_plan(self, date: datetime) -> Schedule:
        """Create a schedule for a particular date."""
        tasks = [t for t in self.pending_tasks() if t.is_due(date)]
        # sort by time while keeping high-priority first if same time
        tasks = sorted(tasks, key=lambda t: (t.start or datetime.max, -t.priority))

        plan = Schedule(date=date, tasks=tasks)
        plan.explanation = f"Generated {len(tasks)} tasks for {date.date()} sorted by time and priority."
        return plan

    def apply_constraints(self):
        """Apply constraints to pending tasks."""
        # Placeholder for constraint handling (e.g., owner availability, max daily hours)
        return self.pending_tasks()

    def rank_tasks(self) -> List[Task]:
        """Rank tasks by priority and schedule order."""
        tasks = self.apply_constraints()
        return sorted(tasks, key=lambda t: (-t.priority, t.start or datetime.max))

    def slot_tasks(self, date: datetime) -> Schedule:
        """Organize tasks into a slot-based daily schedule."""
        plan = self.generate_daily_plan(date)
        # Slotting is basic: keep current start times, maintain order
        # In 2nd iteration, could fill empty slots with unscheduled tasks
        return plan

    def inspect_conflicts(self) -> List[str]:
        """Find conflicting tasks that overlap in time and return warnings."""
        warnings = []
        tasks = [t for t in self.all_tasks() if t.start and t.end]
        tasks_sorted = sorted(tasks, key=lambda x: x.start)

        # lightweight O(n^2) conflict scan for overlaps in same day
        for i, current in enumerate(tasks_sorted):
            for nxt in tasks_sorted[i + 1:]:
                if nxt.start >= current.end:
                    break
                # any overlap
                if nxt.start < current.end:
                    pet_desc_curr = current.assigned_pet.name if current.assigned_pet else 'Unknown'
                    pet_desc_next = nxt.assigned_pet.name if nxt.assigned_pet else 'Unknown'
                    warnings.append(
                        f"WARNING: '{current.title}' ({pet_desc_curr}) [{current.start.strftime('%H:%M')}-{current.end.strftime('%H:%M')}] "
                        f"overlaps with '{nxt.title}' ({pet_desc_next}) [{nxt.start.strftime('%H:%M')}-{nxt.end.strftime('%H:%M')}]"
                    )
        return warnings

