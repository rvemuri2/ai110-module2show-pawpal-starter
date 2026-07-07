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

    # Add tasks with different durations to each pet
    mochi.add_task(Task("1", "Morning walk", 20, Priority.HIGH, "exercise"))
    mochi.add_task(Task("2", "Give meds", 5, Priority.HIGH, "health", is_flexible=False))
    mochi.add_task(Task("3", "Play fetch", 15, Priority.MEDIUM, "enrichment"))

    luna.add_task(Task("4", "Brush fur", 10, Priority.LOW, "grooming"))
    luna.add_task(Task("5", "Feed breakfast", 5, Priority.HIGH, "feeding", is_flexible=False))
    luna.add_task(Task("6", "Laser pointer playtime", 15, Priority.MEDIUM, "enrichment"))

    scheduler = Scheduler()

    # Build and print today's schedule for each pet
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