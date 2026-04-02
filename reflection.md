# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Classes and responsibilities in the initial design:

- `Owner`: holds owner profile, availability windows, and care preferences. Responsible for availability checking and updating owner settings.
- `Pet`: holds pet identity and care-related details (type, age, breed, special needs) and reference to owner. Responsible for profile updates and medication due checks, and a human-readable description.
- `Task` (aka `CareTask`): tracks task metadata (title, duration, priority, time window, assigned pet, status). Responsible for rescheduling, priority updates, completion marking, and due checks.
- `Scheduler`: orchestrates plan creation from a task pool with constraints, ranks and slots tasks, detects conflicts, and generates a daily schedule.

- Core user actions:
  1. Add a pet and owner info: the user should be able to register pet details and owner preferences before task planning.
  2. Add/edit pet care tasks: the user should be able to add tasks such as walks, feeding, meds, grooming with duration and priority and edit them as needed.
  3. Generate and view today’s plan: the user should be able to generate a daily schedule that respects constraints and priorities and inspect today’s tasks (including an explanation of scheduling choices).

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

- Added `Owner.pets: List[Pet]` and `Owner.add_pet()` to ensure owner/pet relationships are bidirectional and easier to traverse in UI and logic.
- Replaced `Task.time_window: Optional[str]` with explicit `Task.start` and `Task.end` datetimes and added `repeat_interval` for recurring tasks to avoid brittle string parsing and support robust scheduling.
- Updated `Scheduler` to accept `pets: List[Pet]` (instead of a single `pet`) to support multi-pet households.
- Added a `Schedule` data class for plan output containing tasks and explanation, separating compute logic from representation.
- Added `Task.create_next_occurrence()` and `Scheduler.mark_task_complete()` for automatic recurring task propagation.
- Added `Scheduler.sort_by_time()`, `Scheduler.filter_tasks()`, and `Scheduler.inspect_conflicts()` for smart scheduling features.

**c. Final UML Diagram**

A comprehensive UML diagram has been created (see `uml_diagram.md`) that reflects the final implementation. Key classes, attributes, and methods are documented, showing how tasks, pets, owners, and the scheduler interact. The diagram confirms that the final design successfully supports multi-pet scheduling, recurring tasks, and conflict detection.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

- Current conflict detection scans tasks sequentially by `start` and flags overlaps only when `next.start < current.end` (a lightweight window-based check). It does not perform complete interval graph optimization or deep constraint solving, which is a deliberate tradeoff for simplicity and maintainability.
- This tradeoff is reasonable because PawPal is intended as a small personal schedule assistant for pet owners; returning warnings rather than raising errors keeps user experience smooth while allowing the owner to quickly resolve timing overlap issues.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
