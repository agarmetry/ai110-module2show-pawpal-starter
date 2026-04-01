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

## Smarter Scheduling

Three features were added to `pawpal_system.py` and demonstrated in `main.py` to make scheduling more useful for a real pet owner:

**Recurring task auto-scheduling**
When a `daily` or `weekly` task is marked complete, `mark_complete()` automatically appends a fresh copy to the pet's task list (`Litter box cleaning` becomes `Litter box cleaning (tomorrow)`). This means the owner never has to manually re-enter repeating tasks.

**Completed task filtering**
`build_schedule()` now skips any task where `completion_status` is `True`, so tasks already done earlier in the day don't consume time budget or clutter the plan.

**Conflict detection**
`Scheduler.detect_conflicts(tasks)` checks a list of tasks for two types of problems without crashing the program:
- *Time-window overlap* — any two tasks whose `[start_time, start_time + duration)` intervals intersect, across any pets
- *Same-slot conflict* — two tasks for the same pet both tagged `"morning"` or `"evening"`, which can't run simultaneously

Warnings are returned as plain strings so they can be printed, logged, or surfaced in the UI without interrupting the rest of the scheduling flow.

## Testing PawPal+

### Running the tests

```bash
python -m pytest
```

### What the tests cover

| Area | Tests |
|---|---|
| **Sorting correctness** | `sort_by_time()` returns tasks in ascending duration order; `organize_tasks()` enforces the full mandatory → priority → duration sort order |
| **Recurrence logic** | Marking a `daily` or `weekly` task complete appends exactly one new task to the pet's list with the correct label; non-recurring frequencies (`morning`, `evening`) produce no new task |
| **Conflict detection** | Overlapping time windows are flagged; adjacent (non-overlapping) windows are not; same-pet same-slot duplicates are flagged; different-pet same-slot tasks are not |
| **Schedule building** | Tasks at exactly the time budget are scheduled; tasks 1 minute over are skipped; zero-budget owners skip everything; empty pet lists produce an empty schedule |
| **Edge cases** | `mark_complete()` with no associated pet does not crash; `detect_conflicts([])` returns an empty list |

24 tests, all passing.

### Confidence Level

★★★★☆ (4/5)

The core scheduling logic — sorting, greedy budget allocation, recurring task generation, and conflict detection — is fully covered and all 24 tests pass. One star is withheld because the greedy algorithm is not optimal (a mandatory task can block multiple smaller tasks that would fit), and the Streamlit UI layer in `app.py` has no test coverage. Reliability of the scheduling engine itself is high.

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
