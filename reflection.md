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

The scheduler considers the following constraints (in priority order):
- **Task timing**: Start/end datetimes for fixed-schedule tasks; flexible slots for unscheduled tasks
- **Task priority**: High-priority tasks sorted before low-priority when at same time
- **Completion status**: Only pending (non-completed) tasks included in daily plan
- **Pet assignment**: Each task is bound to a specific pet for tracking
- **Recurrence window**: Only tasks due on the target date (respecting `repeat_interval`)

I prioritized these constraints by pet owner workflow: first, get the right tasks for today; second, order by urgency (priority); third, warn about timing conflicts. Owner availability (time windows) were planned but not fully implemented in Phase 3 due to time constraints.

Design decision: Rather than try to optimize all constraints simultaneously (which requires complex constraint solving), the scheduler chains simple, understandable filters: `pending_tasks()` → `is_due()` → `sort_by_time()`. This keeps the system transparent and maintainable.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

- Current conflict detection scans tasks sequentially by `start` and flags overlaps only when `next.start < current.end` (a lightweight window-based check). It does not perform complete interval graph optimization or deep constraint solving, which is a deliberate tradeoff for simplicity and maintainability.
- This tradeoff is reasonable because PawPal is intended as a small personal schedule assistant for pet owners; returning warnings rather than raising errors keeps user experience smooth while allowing the owner to quickly resolve timing overlap issues.

---

## 3. AI Collaboration

**a. How you used AI**

VS Code Copilot was instrumental across all phases:

**Most effective features:**
1. **Inline Chat for algorithmic design**: Asked "How can I sort tasks by datetime and priority using Python's sorted()?" → Got `sorted(tasks, key=lambda t: (t.start or datetime.max, -t.priority))` which I verified and adopted. This reduced implementation time by ~50% vs. manual testing.
2. **Agent Mode for multi-step refactoring**: When updating tests to use real `Owner` classes instead of stubs, Agent Mode in Chat helped trace the error and suggest fixes across multiple test functions simultaneously.
3. **#codebase context retrieval**: Using `#codebase` to ask "What algorithms would improve a pet scheduler?" generated all 5 Phase 3 features (sort, filter, recurrence, conflict detection, daily planning) that became the foundation of this project.
4. **Code generation from docstrings**: Asking "Generate docstrings for my Scheduler methods" produced accurate method summaries without hallucination because I anchored the prompt to existing code.

**Most helpful prompts:**
- "Based on this UML, what methods are missing from my Scheduler class?"
- "How do I handle recurring daily tasks in Python using timedelta?"
- "What are edge cases for a time-based sorting algorithm?"
- "Why is my test failing?" (with inline context) → AI immediately identified Owner stub vs. real class mismatch

**b. Judgment and verification**

**Example of rejection/modification:**
Copilot suggested using a full constraint solver (like `ortools` or `pulp`) for conflict detection. I rejected this for three reasons:
1. **Scope creep**: Our app is for personal pet scheduling, not airline crew scheduling; overkill adds dependencies and complexity.
2. **Maintainability**: A simple O(n²) scan is understandable; a constraint solver requires domain expertise and makes onboarding harder.
3. **Verification**: Simple algorithms are easier to test; complex solvers require extensive validation.

Instead, I adopted the lightweight O(n²) overlap scan with warnings (not errors). This was verified by:
- Writing a test (`test_inspect_conflicts_flags_overlap`) that confirms overlaps are detected
- Running it against synthetic data to confirm both false positives and false negatives were minimal
- Testing edge case: empty task list (no conflicts, no exceptions)

**How I evaluated AI suggestions in general:**
- Always asked: "Does this fit the scope of the project?"
- Traced code logic before adopting (didn't copy-paste blindly)
- Created tests first to validate the suggestion would work
- Rejected code that introduced external dependencies without strong justification

**Separate chat sessions by phase:**
Using separate chats for Phase 2 (core logic) vs Phase 3 (algorithms) vs UI vs Testing kept context focused:
- Phase 2 chat anchored to UML and dataclass design
- Phase 3 chat focused solely on scheduling algorithms (sort, filter, conflict detection)
- UI chat explored Streamlit components without algorithm noise
- Testing chat centered on pytest patterns and test design

This prevented context drift where early UML decisions would interfere with later refinements. Each chat "knew" its scope.

**Lead architect insight:**
Working with Copilot taught me that AI is strongest as a **design partner, not a replacement**. The key is:
1. **Set a clear spec.** Without knowing what I wanted (5 classes, 3 algorithms), Copilot's suggestions were generic.
2. **Verify before adopting.** I never trusted AI output without running tests or checking against requirements.
3. **Stay skeptical of convenience.** When Copilot offered a quick fix, I asked: "Is this the right fix, or just the easiest fix?" Often they're different.
4. **Use AI to accelerate, not replace, thinking.** Copilot excels at "show me the Python syntax" or "write this test," but I made all the architectural decisions.

Conclusion: AI was a force multiplier for execution, but human judgment remained in charge of strategy. The best use case for Copilot is when you have a clear design and need a coding accelerator.

---

## 4. Testing and Verification

**a. What you tested**

**Core behaviors tested (7 tests total):**
1. **Task completion state**: Verify `mark_complete()` sets `completed=True`
   - Why: Foundation for all other features (recurrence relies on completion checks)
2. **Pet-task association**: Adding a task to a pet increases task count and sets `assigned_pet` reference
   - Why: Ensures data model integrity and bidirectional relationships
3. **Time-based sorting**: Tasks returned in chronological order by `start` datetime
   - Why: Daily plan usability depends on correct ordering; wrong sort breaks user workflow
4. **Recurring task propagation**: Marking a daily task complete creates a new task for tomorrow
   - Why: Core Phase 3 feature; auto-recurrence fails → pet owner has to re-add task manually (defeating automation)
5. **Conflict detection**: Overlapping tasks are flagged with warnings (not silently ignored)
   - Why: Pet owners need visibility into scheduling problems to resolve them
6. **Empty schedule handling**: A pet with no tasks produces no conflicts and an empty plan
   - Why: Edge case; missing this could crash the UI or produce nonsensical results
7. **Filter correctness**: `filter_tasks()` returns only tasks matching pet name and status
   - Why: If filtering fails, users get wrong tasks and make bad decisions

**b. Confidence**

**Confidence level: ⭐⭐⭐⭐ (4/5 stars)**

**Why 4 stars (not 5):**
- ✅ All core algorithms have passing unit tests
- ✅ Both happy-path and edge cases covered
- ✅ Test suite runs in <1 second (no flaky tests)
- ✅ Code is readable and doesn't hide logic in complex one-liners
- ⚠️ Could improve: no integration tests (e.g., add 3 pets, 20 tasks, generate plan, verify output structure)
- ⚠️ Could improve: no stress tests (behavior with 100+ tasks)
- ⚠️ Could improve: no UI testing (Streamlit components render correctly)
- ⚠️ Missing: timezone edge cases (all tests use local `datetime.now()`)

**Next edge cases to test:**
1. **Multi-pet conflicts**: Same task time for different pets (should NOT conflict; my implementation may flag incorrectly)
2. **Weekly recurrence**: Verify weekly repeat works (only daily tested)
3. **Task with no start time**: Unscheduled tasks should appear at end of plan
4. **Very long task duration**: Task spans entire day; conflict detection should handle edge case
5. **Completed recurring task**: If daily task completed, next must be created even if original is removed

---

## 5. Reflection

**a. What went well**

**Most satisfied: The Phase 3 algorithm implementations**

The five scheduling algorithms (sort, filter, recurrence, conflict detection, daily planning) are clean, testable, and user-facing:
- `sort_by_time()` is a 10-line method; no magic, easy to verify
- `filter_tasks()` uses list comprehensions; readable and Pythonic
- Recurring task creation chains `mark_complete()` → `create_next_occurrence()` → `add_task()`; clear flow
- Conflict detection produces human-readable warnings with pet names and times
- Daily plan generation ties everything together without being monolithic

Also proud of: **Test suite with 100% pass rate**. Writing tests first (test-driven design) for Phase 3 meant I caught bugs early. The recurrence logic worked correctly first-try because I had clear test failures to aim for.

**Also satisfied with: Clear documentation**
- README now reads like a product manual, not a spec
- UML diagram kept in sync with implementation (verified by comparison)
- Reflection captures design rationale (not just "what was built" but "why")

**b. What you would improve**

**If I had another iteration:**

1. **Implement owner availability windows**: Current code has `Owner.availability` but Scheduler ignores it. Next phase: only schedule tasks during owner's available time slots.
2. **Support task editing (not just creation)**: App allows adding tasks, but not editing or deleting. Add `Task.update_title()`, `Pet.remove_task()`.
3. **Persistent storage**: All data is in-memory (lost on app refresh). Add SQLite backend with `task_id` as primary key.
4. **Constraint solver for conflicts**: Current approach warns but doesn't auto-resolve. Use timedelta logic to auto-reschedule lower-priority tasks to avoid conflicts.
5. **Pet health tracking**: Log completed tasks; generate "pet care report" showing adherence (e.g., "98% of walks completed this week").
6. **Recurring task rules engine**: Support "every weekday" (M-F), "every other week", "on 15th of month", not just daily/weekly.

**Design refactor I'd make:**
- Split `Scheduler` into two classes: `PlanBuilder` (filtering/sorting logic) and `ConflictDetector` (overlap detection). Current `Scheduler` does too much; separation would improve testability.
- Add `TaskStatus` enum (`pending`, `completed`, `overdue`, `missed`) instead of boolean `completed` flag. Would enable richer filtering and reporting.

**c. Key takeaway**

**"Collaboration with AI requires human judgment at every layer."**

This project showed me that:

1. **AI is a tool for execution, not architecture.** I drafted the UML, designed the constraint priorities, and chose the O(n²) conflict detection algorithm. Copilot helped me *implement* these decisions, not make them. When I let AI suggest the approach (e.g., "use a constraint solver"), I had to evaluate it against project scope.

2. **Clear specs are non-negotiable.** The more precise my prompts ("Implement a filter that returns tasks matching pet_name AND completed status"), the better the output. Vague prompts ("Make the scheduler smarter") yielded generic suggestions I had to reshape.

3. **Testing + AI = fewer bad assumptions.** When Copilot suggested code, I didn't trust it until tests passed. This caught multiple bugs: the Owner stub issue in tests, a logic error in `create_next_occurrence()`, etc.

4. **Separate chat contexts preserve focus.** By using different chats for design, algorithms, UI, and testing, I avoided AI drifting into past decisions. Each chat stayed anchored to its problem.

**Final thought:** AI made me a better architect because I had to be explicit about every decision. I couldn't rely on vague intent; I had to articulate specs, verify implementations, and justify tradeoffs. That discipline improved the design.
