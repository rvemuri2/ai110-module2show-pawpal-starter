"""
main.py

Temporary testing ground for verifying that the PawPal+ classes and
scheduling logic work correctly from the terminal, before wiring
anything into the Streamlit UI.
"""

from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def main():
    # Create an owner
    owner = Owner("Jordan")
    owner.set_preference("preferred_walk_time", "morning")

    # Create at least two pets
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Add tasks deliberately OUT OF ORDER by fixed_time, to prove sort_by_time
    # actually sorts rather than just echoing back insertion order.
    mochi.add_task(Task("1", "Evening walk", 20, Priority.HIGH, "exercise", is_flexible=False, fixed_time="18:00"))
    mochi.add_task(Task("2", "Give meds", 5, Priority.HIGH, "health", is_flexible=False, fixed_time="08:00"))
    mochi.add_task(Task("3", "Play fetch", 15, Priority.MEDIUM, "enrichment"))  # no fixed_time
    mochi.add_task(Task("4", "Midday check-in", 5, Priority.LOW, "enrichment", is_flexible=False, fixed_time="12:30"))

    luna.add_task(Task("5", "Feed dinner", 5, Priority.HIGH, "feeding", is_flexible=False, fixed_time="19:00"))
    luna.add_task(Task("6", "Feed breakfast", 5, Priority.HIGH, "feeding", is_flexible=False, fixed_time="07:00"))
    luna.add_task(Task("7", "Laser pointer playtime", 15, Priority.MEDIUM, "enrichment"))

    scheduler = Scheduler()

    # --- Demo: sort_by_time ---
    print("=== Mochi's tasks sorted by time (were added out of order) ===")
    for task in scheduler.sort_by_time(mochi.get_tasks()):
        time_label = task.fixed_time if task.fixed_time else "no fixed time"
        print(f"  {time_label:>15}  |  {task.title}")

    # --- Demo: filter_tasks ---
    mochi.get_tasks()[1].mark_complete()  # mark "Give meds" as done

    print("\n=== Filtering demo ===")
    pending_mochi_tasks = scheduler.filter_tasks(
        mochi.get_tasks(), completed=False, pet_name="Mochi"
    )
    print("Mochi's pending tasks:", [t.title for t in pending_mochi_tasks])

    completed_mochi_tasks = scheduler.filter_tasks(
        mochi.get_tasks(), completed=True, pet_name="Mochi"
    )
    print("Mochi's completed tasks:", [t.title for t in completed_mochi_tasks])

    all_tasks = mochi.get_tasks() + luna.get_tasks()
    only_lunas_tasks = scheduler.filter_tasks(all_tasks, pet_name="Luna")
    print("Luna's tasks (filtered out of a combined list):", [t.title for t in only_lunas_tasks])

    # --- Demo: recurring tasks auto-spawn their next occurrence ---
    print("\n=== Recurring task demo ===")

    daily_med = Task(
        "8", "Daily medication", 5, Priority.HIGH, "health",
        is_flexible=False, fixed_time="09:00", frequency="daily",
    )
    mochi.add_task(daily_med)
    print(f"Mochi's task count before completing '{daily_med.title}':", len(mochi.get_tasks()))
    print(f"'{daily_med.title}' due date:", daily_med.due_date)

    next_occurrence = mochi.mark_task_complete(daily_med)

    print(f"Mochi's task count after completing '{daily_med.title}':", len(mochi.get_tasks()))
    print(f"Original task completed: {daily_med.completed}")
    print(f"New task auto-created: '{next_occurrence.title}', due {next_occurrence.due_date}, completed={next_occurrence.completed}")

    weekly_groom = Task(
        "9", "Grooming", 30, Priority.MEDIUM, "grooming", frequency="weekly",
    )
    luna.add_task(weekly_groom)
    next_weekly = luna.mark_task_complete(weekly_groom)
    print(f"\n'{weekly_groom.title}' (weekly) completed. Next occurrence due: {next_weekly.due_date}")

    # --- Demo: conflict detection ---
    # Two tasks scheduled at the SAME TIME on purpose, one pair for the same
    # pet, one pair across two different pets, to prove both cases are caught.
    print("\n=== Conflict detection demo ===")

    # Same-pet conflict: both belong to Mochi, same fixed_time.
    mochi.add_task(
        Task("10", "Nail trim", 15, Priority.LOW, "grooming", is_flexible=False, fixed_time="10:00")
    )
    mochi.add_task(
        Task("11", "Training session", 20, Priority.MEDIUM, "enrichment", is_flexible=False, fixed_time="10:00")
    )

    same_pet_warning = scheduler.check_for_conflicts(mochi.get_tasks())
    print("Checking Mochi's own tasks for conflicts:")
    print(same_pet_warning if same_pet_warning else "  No conflicts found.")

    # Cross-pet conflict: one task on Mochi, one on Luna, same fixed_time,
    # relevant if one owner is trying to handle both pets at once.
    mochi.add_task(
        Task("12", "Vet drop-off", 10, Priority.HIGH, "health", is_flexible=False, fixed_time="15:00")
    )
    luna.add_task(
        Task("13", "Vet pickup", 10, Priority.HIGH, "health", is_flexible=False, fixed_time="15:00")
    )

    all_owner_tasks = owner.get_tasks()  # combined across every pet
    cross_pet_warning = scheduler.check_for_conflicts(all_owner_tasks)
    print("\nChecking ALL of Jordan's tasks (both pets combined) for conflicts:")
    print(cross_pet_warning if cross_pet_warning else "  No conflicts found.")

    # --- Full daily schedule per pet (unchanged from before) ---
    for pet in owner.pets:
        print(f"\n=== Today's Schedule for {pet.name} ({pet.species}) ===")

        plan = scheduler.generate_plan(
            tasks=pet.get_tasks(),
            available_minutes=45,
            preferences=owner.preferences,
            start_time="08:00",
        )

        print(f"Total minutes used: {plan['total_minutes_used']} / 45\n")

        for entry in plan["timeline"]:
            task = entry["task"]
            print(f"  {entry['start']} - {entry['end']}  |  {task.title}")

        if plan["unscheduled"]:
            print("\n  Could not fit today:")
            for task in plan["unscheduled"]:
                print(f"    - {task.title} ({task.duration_minutes} min)")

        print()
        print(plan["reasoning"])


if __name__ == "__main__":
    main()