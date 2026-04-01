import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Task


# --- Task Completion ---

def test_mark_complete_changes_status():
    """Calling mark_complete() should set completion_status to True."""
    task = Task(description="Walk the dog", time=30, frequency="morning")
    assert task.completion_status is False
    task.mark_complete()
    assert task.completion_status is True


# --- Task Addition ---

def test_adding_task_increases_pet_task_count():
    """Appending a task to a pet's task list should increase its task count."""
    pet = Pet(name="Buddy", species="dog", age=3)
    initial_count = len(pet.tasks)
    new_task = Task(description="Vet checkup", time=60, frequency="monthly", pet=pet)
    pet.tasks.append(new_task)
    assert len(pet.tasks) == initial_count + 1
