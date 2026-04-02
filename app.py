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
    priority_map = {"low": 1, "medium": 5, "high": 10}

    if st.button("Add task") and selected_pet:
        task_id = f"{selected_pet_name}-{len(selected_pet.tasks) + 1}"
        new_task = Task(
            id=task_id,
            title=task_title,
            duration=int(task_duration),
            priority=priority_map[task_priority],
        )
        selected_pet.add_task(new_task)
        st.success(f"Task '{task_title}' added to {selected_pet_name}")

    if selected_pet and selected_pet.tasks:
        st.write(f"Tasks for {selected_pet.name}:")
        st.table([
            {"id": t.id, "title": t.title, "duration": t.duration, "priority": t.priority, "completed": t.completed}
            for t in selected_pet.tasks
        ])
    else:
        st.info("No tasks yet for selected pet.")

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
