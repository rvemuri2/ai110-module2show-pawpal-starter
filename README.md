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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
=== Today's Schedule for Mochi (dog) ===
Total minutes used: 40 / 45

08:00 AM - 08:05 AM | Give meds
08:05 AM - 08:25 AM | Morning walk
08:25 AM - 08:40 AM | Play fetch

Scheduled tasks (in order):

- 08:00 AM - 08:05 AM: Give meds (5 min), included because it's high priority and fixed-time commitment.
- 08:05 AM - 08:25 AM: Morning walk (20 min), included because it's high priority.
- 08:25 AM - 08:40 AM: Play fetch (15 min), included because it's medium priority.

=== Today's Schedule for Luna (cat) ===
Total minutes used: 30 / 45

08:00 AM - 08:05 AM | Feed breakfast
08:05 AM - 08:20 AM | Laser pointer playtime
08:20 AM - 08:30 AM | Brush fur

Scheduled tasks (in order):

- 08:00 AM - 08:05 AM: Feed breakfast (5 min), included because it's high priority and fixed-time commitment.
- 08:05 AM - 08:20 AM: Laser pointer playtime (15 min), included because it's medium priority.
- 08:20 AM - 08:30 AM: Brush fur (10 min), included because it's low priority.
```

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

Description of tests: This suite has thirteen tests covering five areas: basic task/pet mechanics (marking complete, adding tasks), sorting (chronological order, flexible tasks sorting last), recurring tasks (daily/weekly spawning the correct next due date, one-off tasks not duplicating, and recurrence working even without a pet attached), conflict detection (flagging same-time tasks, correctly ignoring back-to-back tasks, and returning a clean empty string when nothing overlaps), and scheduling edge cases (empty task lists and tasks too long to fit the time budget, both handled gracefully instead of crashing).

```bash
# Run the full test suite:
pytest
python -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:
collected 13 items

tests/test_pawpal.py ............. [100%]

================================= 13 passed in 0.02s ==================================

```
# Paste your pytest output here

collected 13 items

tests/test_pawpal.py::test_task_completion PASSED                               [  7%]
tests/test_pawpal.py::test_task_addition_increases_pet_task_count PASSED        [ 15%]
tests/test_pawpal.py::test_daily_task_spawns_next_occurrence_due_tomorrow PASSED [ 23%]
tests/test_pawpal.py::test_non_recurring_task_does_not_spawn_next_occurrence PASSED [ 30%]
tests/test_pawpal.py::test_weekly_task_spawns_next_occurrence_due_in_seven_days PASSED[ 38%]
tests/test_pawpal.py::test_recurring_task_without_a_pet_does_not_crash PASSED   [ 46%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED      [ 53%]
tests/test_pawpal.py::test_sort_by_time_puts_flexible_tasks_last PASSED         [ 61%]
tests/test_pawpal.py::test_detect_conflicts_flags_duplicate_times PASSED        [ 69%]
tests/test_pawpal.py::test_detect_conflicts_ignores_back_to_back_tasks PASSED   [ 76%]
tests/test_pawpal.py::test_check_for_conflicts_returns_empty_string_when_no_conflicts PASSED [ 84%]
tests/test_pawpal.py::test_generate_plan_with_no_tasks_does_not_crash PASSED    [ 92%]
tests/test_pawpal.py::test_generate_plan_skips_task_that_does_not_fit_budget PASSED [100%]


I'd rate this a 4 out of 5 stars. The tests are specific and deterministic rather than vague, and they cover the riskiest logic well, recurrence date math, conflict boundary conditions, and sorting, along with solid edge cases like empty task lists and missing pet references. It falls short of 5 because there's no full integration test exercising generate_plan() end-to-end with a realistic mix of tasks, and a few methods (filter_tasks(), Owner.get_tasks(), Pet.mark_task_complete()) have no test coverage at all yet.
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature           | Method(s) | Notes                             |
| ----------------- | --------- | --------------------------------- |
| Task sorting      |           | e.g., by priority, duration       |
| Filtering         |           | e.g., skip tasks if time runs out |
| Conflict handling |           | e.g., overlapping time slots      |
| Recurring tasks   |           | e.g., daily vs. weekly            |

I'm going to fill in the table by creating a new table:
![table](./image.png)

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or link to a demo video here -->
