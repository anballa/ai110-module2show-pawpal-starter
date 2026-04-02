# PawPal+ Final UML Diagram

```mermaid
classDiagram
    class Task {
        -id: str
        -title: str
        -duration: int
        -priority: int
        -start: Optional[datetime]
        -end: Optional[datetime]
        -assigned_pet: Optional[Pet]
        -completed: bool
        -repeat_interval: Optional[str]
        +reschedule(start, end)
        +update_priority(level)
        +mark_complete()
        +create_next_occurrence()
        +is_due(date)
    }

    class Pet {
        -name: str
        -type: str
        -age: int
        -breed: str
        -special_needs: Optional[str]
        -owner_ref: Optional[Owner]
        -tasks: List~Task~
        +update_profile(**kwargs)
        +needs_medication_now(at_time)
        +describe()
        +add_task(task)
        +remove_task(task_id)
        +get_tasks()
    }

    class Owner {
        -name: str
        -contact: str
        -availability: List[str]
        -preferences: Dict[str, str]
        -pets: List~Pet~
        +add_pet(pet)
        +update_availability(availability)
        +update_preferences(preferences)
        +is_available(time_slot)
        +get_all_tasks()
    }

    class Schedule {
        -date: datetime
        -tasks: List~Task~
        -explanation: Optional[str]
    }

    class Scheduler {
        -owner: Owner
        -pets: List~Pet~
        -constraints: Dict
        +all_tasks()
        +pending_tasks()
        +mark_task_complete(task_id)
        +sort_by_time(tasks)
        +filter_tasks(pet_name, completed)
        +generate_daily_plan(date)
        +apply_constraints()
        +rank_tasks()
        +slot_tasks(date)
        +inspect_conflicts()
    }

    %% Relationships
    Owner "1" --> "*" Pet : has
    Pet "1" --> "*" Task : manages
    Task --> Pet : assigned_to
    Pet --> Owner : belongs_to
    Scheduler --> Owner : orchestrates
    Scheduler --> Schedule : produces
    Scheduler --> Task : processes

    %% Aggregation notes
    note for Scheduler "Coordinates scheduling logic:
    - Sorts tasks by time
    - Filters by pet/status
    - Detects conflicts
    - Handles recurring tasks"

    note for Task "Supports recurrence:
    - daily/weekly repeats
    - Auto-generates next
    - Tracks completion"

    note for Owner "Central hub:
    - Manages pets
    - Aggregates all tasks
    - Tracks availability"
```

## Key Enhancements from Phase 1 to Final Implementation

### New Attributes Added
- **Task**: `repeat_interval` (for daily/weekly recurrence)
- **Task**: `end` datetime (for conflict detection window)

### New Methods Added
- **Task**: `create_next_occurrence()` (auto-schedule repeats)
- **Task**: `is_due(date)` (date filtering)
- **Scheduler**: `sort_by_time(tasks)` (algorithmic sorting)
- **Scheduler**: `filter_tasks(pet_name, completed)` (filtering logic)
- **Scheduler**: `mark_task_complete(task_id)` (with recurrence automation)
- **Scheduler**: `inspect_conflicts()` (lightweight conflict detection)

### Relationship Changes
- Task now maintains back-reference to assigned Pet
- Pet maintains reference to Owner for bidirectional lookup
- Scheduler created as separate orchestration class (not mixed with Owner)
- Schedule dataclass created as explicit output type

### Architecture Insights
- **Separation of Concerns**: Scheduler is separate from Owner/Pet data classes
- **Recurrence Automation**: Tasks auto-create next occurrence on completion
- **Conflict Reporting**: Non-blocking warnings (not exceptions)
- **Filtering Support**: Query tasks by pet, completion status, or both
