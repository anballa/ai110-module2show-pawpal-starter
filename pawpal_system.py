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
        """Mark this task as complete."""
        self.completed = True

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

    def generate_daily_plan(self, date: datetime) -> Schedule:
        """Create a schedule for a particular date."""
        tasks = [t for t in self.pending_tasks() if t.is_due(date)]
        sorted_tasks = sorted(tasks, key=lambda t: (-t.priority, t.start or datetime.max))
        plan = Schedule(date=date, tasks=sorted_tasks)
        plan.explanation = f"Generated {len(sorted_tasks)} tasks for {date.date()} sorted by priority and time."
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
        """Find conflicting tasks that overlap in time."""
        conflicts = []
        tasks = [t for t in self.all_tasks() if t.start and t.end]
        tasks_sorted = sorted(tasks, key=lambda x: x.start)
        for i in range(len(tasks_sorted) - 1):
            current = tasks_sorted[i]
            nxt = tasks_sorted[i + 1]
            if current.end and nxt.start and current.end > nxt.start:
                conflicts.append(f"{current.title} overlaps with {nxt.title}")
        return conflicts
