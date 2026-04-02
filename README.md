# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

PawPal+ implements core scheduling algorithms for intelligent pet care planning:

### 🔄 Recurring Tasks
- **Algorithm**: Daily/weekly recurrence with automatic next-occurrence generation
- **Implementation**: `Task.repeat_interval` flag + `Task.create_next_occurrence()` method
- **Behavior**: When a recurring task is marked complete, a new task is automatically scheduled for the next day/week at the same time
- **Use case**: Pet owners can set up daily walks, feeding, or medication once and it repeats automatically

### ⏱️ Time-Based Sorting
- **Algorithm**: Chronological task ordering by start time
- **Implementation**: `Scheduler.sort_by_time()` uses Python's `sorted()` with datetime key function
- **Behavior**: Tasks are returned in ascending order by start time; unscheduled tasks appear last
- **Use case**: Daily plan displays tasks in the order they should be completed

### 🔎 Smart Filtering
- **Algorithm**: Multi-criteria task filtering by pet and completion status
- **Implementation**: `Scheduler.filter_tasks(pet_name=optional, completed=optional)` with list comprehensions
- **Behavior**: Returns only tasks matching selected pet and/or status (pending/completed)
- **Use case**: Pet owners can view tasks for a specific pet or only see what remains to be done

### ⚠️ Conflict Detection
- **Algorithm**: Lightweight interval overlap detection using sequential scanning
- **Implementation**: `Scheduler.inspect_conflicts()` iterates through sorted tasks and flags overlaps
- **Behavior**: Returns warnings (not errors) when two tasks overlap in time; includes pet names and times
- **Tradeoff**: O(n²) scan for simplicity; doesn't require full constraint solver
- **Use case**: Pet owners receive warnings if tasks are scheduled at incompatible times

### 📅 Daily Plan Generation
- **Algorithm**: Filter, sort, and compile a schedule for a given date
- **Implementation**: `Scheduler.generate_daily_plan(date)` chains filtering and sorting
- **Behavior**: Returns `Schedule` object with tasks, date, and human-readable explanation
- **Use case**: Users see today's complete schedule with reasoning for task selection/ordering

## 📸 Demo

Here's the PawPal+ interface in action:

<a href="/course_images/ai110/pawpal_demo.png" target="_blank"><img src='/course_images/ai110/pawpal_demo.png' title='PawPal+ App Demo' width='' alt='PawPal+ App Demo' class='center-block' /></a>

**To run the app locally:**

```bash
streamlit run app.py
```

The Streamlit UI provides:
- Owner and pet management interface
- Task creation with recurrence support (daily/weekly)
- Multiple scheduling views: Daily plan, conflict warnings, filtering
- Recurring task manager for marking tasks complete and auto-scheduling next occurrences

## Smarter Scheduling

Enhancements implemented:

- Sorting tasks by time and priority using `Scheduler.sort_by_time()`
- Filtering tasks by pet name and complete status using `Scheduler.filter_tasks()`
- Recurring task support with `Task.repeat_interval` (`daily`, `weekly`) and auto-recreation via `Scheduler.mark_task_complete()`
- Lightweight conflict detection with warnings via `Scheduler.inspect_conflicts()`


## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

### Run the test suite

```bash
python -m pytest -q
```

### What tests cover

The automated test suite in `tests/test_pawpal.py` includes 7 tests across core scheduling behaviors:

- **Task completion**: Ensures tasks mark as complete when `mark_complete()` is called
- **Pet task management**: Validates task addition to pet profiles
- **Sorting correctness**: Confirms `sort_by_time()` returns tasks in chronological order
- **Recurring task logic**: Verifies daily/weekly tasks auto-create next occurrences after completion
- **Conflict detection**: Validates `inspect_conflicts()` flags overlapping task times
- **Edge cases**: Tests empty pet schedules (no conflicts, empty plans)

### Confidence Level

**⭐⭐⭐⭐ (4/5 stars)**

**Why 4 stars:**
- All core scheduling algorithms (sort, filter, conflict detection, recurrence) have passing tests
- Happy path and edge cases are covered
- Empty state handling tested
- Could improve with: integration tests for multi-pet complex scenarios, boundary tests for time window edge cases, stress tests with 50+ tasks

