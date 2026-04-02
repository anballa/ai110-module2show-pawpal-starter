import streamlit as st
from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Initialize owner object in session state
if "owner_obj" not in st.session_state:
    st.session_state.owner_obj = Owner(name="Jordan", contact="jordan@example.com")

owner = st.session_state.owner_obj

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.name)
owner_contact = st.text_input("Contact", value=owner.contact)
if st.button("Update owner"):
    owner.name = owner_name
    owner.contact = owner_contact
    st.success("Owner info updated")

st.markdown("### Pets")
pet_name = st.text_input("Pet name", value="Mochi")
pet_type = st.selectbox("Species", ["dog", "cat", "other"], index=0)
pet_age = st.number_input("Pet age", min_value=0, max_value=30, value=1)
pet_breed = st.text_input("Breed", value="Unknown")

if st.button("Add pet"):
    new_pet = Pet(name=pet_name, type=pet_type, age=int(pet_age), breed=pet_breed)
    owner.add_pet(new_pet)
    st.success(f"Added pet {pet_name}")

if owner.pets:
    st.write("Current pets:")
    st.table([{"name": p.name, "type": p.type, "age": p.age, "breed": p.breed} for p in owner.pets])
else:
    st.info("No pets yet. Add a pet above.")

st.divider()

st.subheader("Tasks")
if not owner.pets:
    st.warning("Add a pet before creating tasks.")
else:
    selected_pet_name = st.selectbox("Assign task to", [p.name for p in owner.pets])
    selected_pet = next((p for p in owner.pets if p.name == selected_pet_name), None)

    task_title = st.text_input("Task title", value="Morning walk")
    task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    task_priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    task_recurrence = st.selectbox("Repeat", ["none", "daily", "weekly"], index=0)
    priority_map = {"low": 1, "medium": 5, "high": 10}

    if st.button("Add task") and selected_pet:
        task_id = f"{selected_pet_name}-{len(selected_pet.tasks) + 1}"
        new_task = Task(
            id=task_id,
            title=task_title,
            duration=int(task_duration),
            priority=priority_map[task_priority],
            repeat_interval=task_recurrence if task_recurrence != "none" else None,
        )
        selected_pet.add_task(new_task)
        st.success(f"✅ Task '{task_title}' added to {selected_pet_name} ({task_recurrence})")

    if selected_pet and selected_pet.tasks:
        st.write(f"**Tasks for {selected_pet.name}:**")
        task_data = []
        for t in selected_pet.tasks:
            task_data.append({
                "Title": t.title,
                "Duration": f"{t.duration} min",
                "Priority": t.priority,
                "Repeat": t.repeat_interval or "—",
                "Completed": "✓" if t.completed else "○"
            })
        st.table(task_data)
    else:
        st.info("No tasks yet for selected pet.")

st.divider()

st.subheader("Schedule Management")
col1, col2 = st.columns(2)

with col1:
    filter_pet = st.selectbox("Filter tasks by pet", ["All"] + [p.name for p in owner.pets])

with col2:
    filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"])
    status_filter_map = {"All": None, "Pending": False, "Completed": True}

if st.button("Generate & Analyze Schedule"):
    if not owner.pets:
        st.error("❌ Add a pet and tasks to generate a schedule.")
    elif not owner.get_all_tasks():
        st.warning("⚠️ No tasks yet. Add tasks to see a schedule.")
    else:
        scheduler = Scheduler(owner)
        plan = scheduler.generate_daily_plan(datetime.now())

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📅 Today's Schedule (Sorted by Time)")
        with col2:
            st.metric("Total Tasks", len(plan.tasks))

        if plan.tasks:
            schedule_data = []
            for task in plan.tasks:
                pet_name = task.assigned_pet.name if task.assigned_pet else "Unknown"
                schedule_data.append({
                    "Time": task.start.strftime('%H:%M') if task.start else "Flexible",
                    "Task": task.title,
                    "Pet": pet_name,
                    "Priority": task.priority,
                    "Duration (min)": task.duration,
                    "Repeat": task.repeat_interval or "—"
                })
            st.table(schedule_data)
            st.info(f"ℹ️ {plan.explanation}")
        else:
            st.info("No pending tasks for today.")

        # Show conflict warnings
        conflicts = scheduler.inspect_conflicts()
        if conflicts:
            st.subheader("⚠️ Schedule Conflicts Detected")
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("✅ No scheduling conflicts detected.")

st.divider()

st.subheader("Advanced Filters & Recurring Tasks")

if owner.get_all_tasks():
    scheduler = Scheduler(owner)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔍 Filter Tasks")
        selected_filter_pet = st.selectbox("By pet:", ["All"] + [p.name for p in owner.pets], key="filter_pet")
        selected_filter_status = st.selectbox("By status:", ["All", "Pending", "Completed"], key="filter_status")

        pet_filter = selected_filter_pet if selected_filter_pet != "All" else None
        status_filter = None if selected_filter_status == "All" else (selected_filter_status == "Completed")

        filtered = scheduler.filter_tasks(pet_name=pet_filter, completed=status_filter)

        if filtered:
            st.write(f"Found {len(filtered)} task(s)")
            filtered_data = [{
                "Title": t.title,
                "Pet": t.assigned_pet.name if t.assigned_pet else "—",
                "Priority": t.priority,
                "Status": "✓ Done" if t.completed else "Pending"
            } for t in filtered]
            st.table(filtered_data)
        else:
            st.info("No tasks match the selected filters.")

    with col2:
        st.subheader("🔄 Manage Recurring Tasks")
        all_tasks = scheduler.all_tasks()
        recurring_tasks = [t for t in all_tasks if t.repeat_interval]

        if recurring_tasks:
            task_to_mark = st.selectbox("Mark task complete:", [f"{t.title} ({t.assigned_pet.name})" for t in recurring_tasks])
            selected_recurring = recurring_tasks[next(i for i, t in enumerate(recurring_tasks) if f"{t.title} ({t.assigned_pet.name})" == task_to_mark)]

            if st.button("✓ Mark Complete & Schedule Next"):
                next_task = scheduler.mark_task_complete(selected_recurring.id)
                if next_task:
                    st.success(f"✅ '{selected_recurring.title}' marked complete!\n\n📅 Next occurrence scheduled for {next_task.start.strftime('%Y-%m-%d at %H:%M')}")
                else:
                    st.success(f"✅ '{selected_recurring.title}' marked complete (no repeat).")
        else:
            st.info("No recurring tasks yet.")
else:
    st.info("Add tasks to see filter and recurrence options.")

st.divider()

st.subheader("Build Schedule")
if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan(datetime.now())

    if plan.tasks:
        st.write("Today's Schedule")
        for task in plan.tasks:
            pet_name = task.assigned_pet.name if task.assigned_pet else "Unknown"
            st.write(f"- {task.title} for {pet_name} (priority {task.priority})")
        st.write("Explanation:", plan.explanation)
    else:
        st.info("No tasks to schedule right now.")
