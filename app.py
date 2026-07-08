import streamlit as st
from datetime import datetime
from pawpal_system import Owner, Pet, Task, Priority, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# Scheduler is stateless, so one shared instance is reused everywhere:
# for live-sorting the task list, checking conflicts, and generating the plan.
scheduler = Scheduler()

st.markdown(
    """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
)

st.divider()

# ---------------------------------------------------------------------------
# Session state setup
# ---------------------------------------------------------------------------
# st.session_state acts like a persistent dict across reruns. Streamlit reruns
# this whole script on every interaction, so without checking "owner" already
# exists here, a fresh Owner (and all its pets/tasks) would be wiped out every
# time a button is clicked.
if "owner" not in st.session_state:
    st.session_state.owner = None

if "selected_pet_name" not in st.session_state:
    st.session_state.selected_pet_name = None


# ---------------------------------------------------------------------------
# Step 1: Owner setup
# ---------------------------------------------------------------------------
st.subheader("Owner Info")

if st.session_state.owner is None:
    owner_name = st.text_input("Owner name", value="Jordan")
    if st.button("Create Owner"):
        st.session_state.owner = Owner(name=owner_name)
        st.rerun()
    st.info("Create an owner to get started.")
    st.stop()  # nothing below matters until an Owner exists

owner = st.session_state.owner
st.success(f"Owner: **{owner.name}**")

with st.expander("Owner preferences"):
    pref_key = st.text_input("Preference name", value="preferred_walk_time")
    pref_value = st.text_input("Preference value", value="morning")
    if st.button("Save preference"):
        owner.set_preference(pref_key, pref_value)
        st.rerun()

    if owner.preferences:
        st.write(owner.preferences)

st.divider()

# ---------------------------------------------------------------------------
# Step 2: Add a pet
# ---------------------------------------------------------------------------
st.subheader("Pets")

with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    submitted_pet = st.form_submit_button("Add Pet")

    if submitted_pet:
        # Owner.add_pet() appends to owner.pets AND sets pet.owner back-reference.
        new_pet = Pet(name=pet_name, species=species)
        owner.add_pet(new_pet)
        st.session_state.selected_pet_name = new_pet.name
        st.rerun()

if not owner.pets:
    st.info("No pets yet. Add one above.")
    st.stop()

pet_names = [p.name for p in owner.pets]
st.session_state.selected_pet_name = st.selectbox(
    "Select a pet",
    pet_names,
    index=pet_names.index(st.session_state.selected_pet_name)
    if st.session_state.selected_pet_name in pet_names
    else 0,
)
selected_pet = next(p for p in owner.pets if p.name == st.session_state.selected_pet_name)

st.divider()

# ---------------------------------------------------------------------------
# Step 3: Add tasks to the selected pet
# ---------------------------------------------------------------------------
st.subheader(f"Tasks for {selected_pet.name}")

with st.form("add_task_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority_str = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    is_flexible = st.checkbox("Flexible timing (uncheck for fixed-time tasks like meds)", value=True)

    # BUG FIX: previously there was no way to actually enter a fixed_time,
    # so unchecking "Flexible timing" set is_flexible=False but fixed_time
    # stayed None, meaning conflict detection and time-anchoring never
    # actually triggered through the UI. This field only appears when it's
    # relevant, i.e. when the task isn't flexible.
    fixed_time_str = None
    if not is_flexible:
        fixed_time_str = st.text_input(
            "Fixed time (24-hour HH:MM)",
            value="08:00",
            help="The exact clock time this task must happen at.",
        )

    frequency_str = st.selectbox("Repeats", ["none", "daily", "weekly"], index=0)

    submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        # Validate the fixed_time format before creating the task, so a typo
        # like "8am" doesn't silently produce a task that crashes the
        # scheduler later when it tries to parse the time.
        valid_fixed_time = None
        if not is_flexible:
            try:
                datetime.strptime(fixed_time_str, "%H:%M")
                valid_fixed_time = fixed_time_str
            except ValueError:
                st.error(
                    f"'{fixed_time_str}' isn't a valid time. Please use 24-hour "
                    f"HH:MM format (e.g. 08:00 or 17:30). Task was not added."
                )

        if is_flexible or valid_fixed_time:
            # Pet.add_task() appends to that pet's own task list.
            new_task = Task(
                id=str(len(selected_pet.get_tasks()) + 1),
                title=task_title,
                duration_minutes=int(duration),
                priority=Priority(priority_str),
                category="general",
                is_flexible=is_flexible,
                fixed_time=valid_fixed_time,
                frequency=None if frequency_str == "none" else frequency_str,
            )
            selected_pet.add_task(new_task)
            st.rerun()

if selected_pet.get_tasks():
    st.write("Current tasks (sorted by time):")

    # Use Scheduler.sort_by_time() so fixed-time tasks display chronologically;
    # flexible tasks (no fixed time) fall to the end of the list.
    for task in scheduler.sort_by_time(selected_pet.get_tasks()):
        cols = st.columns([1, 3, 1, 1, 1])
        cols[0].write(f"`{task.fixed_time}`" if task.fixed_time else "—")
        cols[1].write(f"**{task.title}** ({task.duration_minutes} min, {task.priority.value})")
        cols[2].write("🔁 " + task.frequency if task.frequency else "one-time")
        cols[3].write("✅ done" if task.completed else "⏳ pending")

        # Mark Pet.mark_task_complete() as the handler: it delegates to
        # Task.mark_complete(), which auto-spawns the next occurrence for
        # daily/weekly tasks and adds it back onto this pet's task list.
        if not task.completed:
            if cols[4].button("Complete", key=f"complete_{task.id}"):
                next_task = selected_pet.mark_task_complete(task)
                if next_task:
                    st.toast(f"Next occurrence of '{task.title}' created, due {next_task.due_date}.")
                st.rerun()

    # Surface conflicts immediately, right where the owner is looking at their
    # tasks, rather than waiting until they click "Generate schedule." A
    # conflict is a contradiction in the data itself (two fixed times can't
    # both happen), so it gets st.error rather than the softer st.warning
    # used for "ran out of time" situations later on.
    conflict_warning = scheduler.check_for_conflicts(selected_pet.get_tasks())
    fixed_time_tasks = [t for t in selected_pet.get_tasks() if t.fixed_time]

    if conflict_warning:
        st.error(conflict_warning)
    elif fixed_time_tasks:
        st.success("✅ No time conflicts among this pet's fixed-time tasks.")
else:
    st.info("No tasks yet for this pet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Step 4: Generate the schedule
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")

available_minutes = st.number_input(
    "Available minutes today", min_value=5, max_value=600, value=45
)
start_time = st.text_input("Start time (24-hour HH:MM)", value="08:00")

if st.button("Generate schedule"):
    if not selected_pet.get_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        # BUG FIX: start_time was passed straight into generate_plan() with no
        # validation. A bad format (e.g. "8am", empty string) would raise an
        # uncaught ValueError inside datetime.strptime() and crash the whole
        # app with a traceback instead of a friendly message.
        try:
            datetime.strptime(start_time, "%H:%M")
            valid_start_time = start_time
        except ValueError:
            valid_start_time = None
            st.error(
                f"'{start_time}' isn't a valid start time. Please use 24-hour "
                f"HH:MM format (e.g. 08:00 or 17:30)."
            )

        if valid_start_time:
            plan = scheduler.generate_plan(
                tasks=selected_pet.get_tasks(),
                available_minutes=int(available_minutes),
                preferences=owner.preferences,
                start_time=valid_start_time,
            )

            st.markdown(f"### Today's Schedule for {selected_pet.name}")
            st.caption(f"Total minutes used: {plan['total_minutes_used']} / {available_minutes}")

            # Conflicts are the most urgent thing to show, surface them first,
            # above the schedule itself, so they can't be missed.
            if plan["conflicts"]:
                conflict_lines = [
                    f"'{a.title}' ({a.fixed_time}) overlaps with '{b.title}' ({b.fixed_time})"
                    for a, b in plan["conflicts"]
                ]
                st.error("⚠️ Scheduling conflicts found:\n\n" + "\n\n".join(conflict_lines))

            if plan["timeline"]:
                st.table(
                    [
                        {
                            "start": entry["start"],
                            "end": entry["end"],
                            "task": entry["task"].title,
                            "priority": entry["task"].priority.value,
                        }
                        for entry in plan["timeline"]
                    ]
                )
            else:
                st.info("No tasks were scheduled with the available time.")

            if plan["unscheduled"]:
                st.warning(
                    "Couldn't fit: " + ", ".join(t.title for t in plan["unscheduled"])
                )
            elif not plan["conflicts"]:
                st.success("🎉 All tasks fit today's schedule with no conflicts!")

            with st.expander("Why this schedule?", expanded=True):
                st.text(plan["reasoning"])