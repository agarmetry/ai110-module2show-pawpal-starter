import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Owner, Task, Scheduler


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


# --- Recurring Tasks: next_occurrence() ---

def test_daily_task_creates_next_occurrence():
    """A daily task should produce a new Task labeled 'tomorrow'."""
    task = Task(description="Feed the cat", time=5, frequency="daily")
    next_task = task.next_occurrence()
    assert next_task is not None
    assert "tomorrow" in next_task.description
    assert next_task.completion_status is False
    assert next_task.frequency == "daily"

def test_weekly_task_creates_next_occurrence():
    """A weekly task should produce a new Task labeled 'next week'."""
    task = Task(description="Flea treatment", time=10, frequency="weekly")
    next_task = task.next_occurrence()
    assert next_task is not None
    assert "next week" in next_task.description

def test_non_recurring_frequency_returns_none():
    """'morning' and 'evening' tasks should return None from next_occurrence()."""
    morning_task = Task(description="Walk the dog", time=30, frequency="morning")
    evening_task = Task(description="Evening walk", time=20, frequency="evening")
    assert morning_task.next_occurrence() is None
    assert evening_task.next_occurrence() is None

def test_mark_complete_appends_to_pet_for_daily():
    """mark_complete() on a daily task with a pet should append one new task to the pet."""
    pet = Pet(name="Whiskers", species="cat", age=2)
    task = Task(description="Feed Whiskers", time=5, frequency="daily", pet=pet)
    pet.tasks.append(task)
    initial_count = len(pet.tasks)
    task.mark_complete()
    assert len(pet.tasks) == initial_count + 1
    assert "tomorrow" in pet.tasks[-1].description

def test_mark_complete_no_pet_does_not_crash():
    """mark_complete() on a daily task with no pet should not raise and should not append anywhere."""
    task = Task(description="Orphan task", time=10, frequency="daily", pet=None)
    task.mark_complete()  # should not raise
    assert task.completion_status is True

def test_non_recurring_mark_complete_does_not_append():
    """mark_complete() on a 'morning' task should not append a next occurrence."""
    pet = Pet(name="Buddy", species="dog", age=3)
    task = Task(description="Walk", time=30, frequency="morning", pet=pet)
    pet.tasks.append(task)
    initial_count = len(pet.tasks)
    task.mark_complete()
    assert len(pet.tasks) == initial_count  # no new task added


# --- Sorting: sort_by_time() — chronological order ---

def test_sort_by_time_returns_ascending_duration():
    """sort_by_time() should return tasks ordered shortest to longest duration."""
    owner = Owner(name="Alex", available_minutes=120)
    scheduler = Scheduler(owner)
    tasks = [
        Task(description="Long", time=60, frequency="daily"),
        Task(description="Short", time=5, frequency="daily"),
        Task(description="Medium", time=30, frequency="daily"),
    ]
    result = scheduler.sort_by_time(tasks)
    durations = [t.time for t in result]
    assert durations == sorted(durations)

def test_sort_by_time_single_task_unchanged():
    """sort_by_time() on a single-element list should return that same task."""
    owner = Owner(name="Alex", available_minutes=60)
    scheduler = Scheduler(owner)
    task = Task(description="Walk", time=30, frequency="morning")
    result = scheduler.sort_by_time([task])
    assert result == [task]


# --- Sorting: organize_tasks() ---

def test_mandatory_tasks_sorted_before_optional():
    """Mandatory tasks should always appear before optional ones regardless of priority."""
    owner = Owner(name="Alex", available_minutes=120)
    scheduler = Scheduler(owner)
    optional_high = Task(description="Optional high", time=10, frequency="daily", priority="high", is_mandatory=False)
    mandatory_low = Task(description="Mandatory low", time=10, frequency="daily", priority="low", is_mandatory=True)
    result = scheduler.organize_tasks([optional_high, mandatory_low])
    assert result[0].is_mandatory is True

def test_higher_priority_sorted_before_lower_among_mandatory():
    """Among mandatory tasks, higher priority should come first."""
    owner = Owner(name="Alex", available_minutes=120)
    scheduler = Scheduler(owner)
    low = Task(description="Low", time=10, frequency="daily", priority="low", is_mandatory=True)
    high = Task(description="High", time=10, frequency="daily", priority="high", is_mandatory=True)
    result = scheduler.organize_tasks([low, high])
    assert result[0].priority == "high"

def test_shorter_task_sorted_first_among_equal_priority():
    """When priority and mandatory status tie, the shorter task should come first."""
    owner = Owner(name="Alex", available_minutes=120)
    scheduler = Scheduler(owner)
    long_task = Task(description="Long", time=60, frequency="daily", priority="medium", is_mandatory=False)
    short_task = Task(description="Short", time=10, frequency="daily", priority="medium", is_mandatory=False)
    result = scheduler.organize_tasks([long_task, short_task])
    assert result[0].time == 10

def test_organize_tasks_full_sort_order():
    """organize_tasks() should order: mandatory-high → mandatory-low → optional-high → optional-low."""
    owner = Owner(name="Alex", available_minutes=120)
    scheduler = Scheduler(owner)
    opt_low  = Task(description="opt_low",  time=10, frequency="daily", priority="low",  is_mandatory=False)
    opt_high = Task(description="opt_high", time=10, frequency="daily", priority="high", is_mandatory=False)
    man_low  = Task(description="man_low",  time=10, frequency="daily", priority="low",  is_mandatory=True)
    man_high = Task(description="man_high", time=10, frequency="daily", priority="high", is_mandatory=True)
    result = scheduler.organize_tasks([opt_low, opt_high, man_low, man_high])
    descriptions = [t.description for t in result]
    assert descriptions == ["man_high", "man_low", "opt_high", "opt_low"]


# --- Schedule Building: build_schedule() ---

def test_task_exactly_at_budget_is_scheduled():
    """A task whose duration exactly equals available_minutes should be scheduled."""
    pet = Pet(name="Buddy", species="dog", age=3)
    task = Task(description="Long walk", time=60, frequency="daily", pet=pet)
    pet.tasks.append(task)
    owner = Owner(name="Alex", available_minutes=60, pets=[pet])
    schedule = Scheduler(owner).build_schedule()
    assert task in schedule.scheduled_tasks

def test_task_one_minute_over_budget_is_skipped():
    """A task that exceeds available_minutes by 1 should be skipped."""
    pet = Pet(name="Buddy", species="dog", age=3)
    task = Task(description="Long walk", time=61, frequency="daily", pet=pet)
    pet.tasks.append(task)
    owner = Owner(name="Alex", available_minutes=60, pets=[pet])
    schedule = Scheduler(owner).build_schedule()
    assert task in schedule.skipped_tasks

def test_empty_task_list_builds_empty_schedule():
    """An owner with no pets should produce a schedule with nothing scheduled."""
    owner = Owner(name="Alex", available_minutes=60, pets=[])
    schedule = Scheduler(owner).build_schedule()
    assert schedule.scheduled_tasks == []
    assert schedule.skipped_tasks == []
    assert schedule.total_duration == 0

def test_zero_budget_skips_all_tasks():
    """An owner with 0 available minutes should skip every task."""
    pet = Pet(name="Buddy", species="dog", age=3)
    task = Task(description="Walk", time=30, frequency="daily", pet=pet)
    pet.tasks.append(task)
    owner = Owner(name="Alex", available_minutes=0, pets=[pet])
    schedule = Scheduler(owner).build_schedule()
    assert schedule.scheduled_tasks == []
    assert len(schedule.skipped_tasks) == 1


# --- Conflict Detection: detect_conflicts() ---

def test_overlapping_time_windows_flagged():
    """Two tasks with overlapping start_time windows should produce a warning."""
    pet = Pet(name="Mochi", species="dog", age=2)
    task_a = Task(description="Walk", time=30, frequency="morning", pet=pet, start_time=480)   # 8:00–8:30
    task_b = Task(description="Feed", time=20, frequency="morning", pet=pet, start_time=495)   # 8:15–8:35
    owner = Owner(name="Alex", available_minutes=120)
    warnings = Scheduler(owner).detect_conflicts([task_a, task_b])
    assert any("Time overlap" in w for w in warnings)

def test_adjacent_time_windows_not_flagged():
    """Tasks that share only an endpoint (A ends exactly when B starts) should not conflict."""
    pet = Pet(name="Mochi", species="dog", age=2)
    task_a = Task(description="Walk", time=30, frequency="morning", pet=pet, start_time=480)   # 8:00–8:30
    task_b = Task(description="Feed", time=20, frequency="morning", pet=pet, start_time=510)   # 8:30–8:50
    owner = Owner(name="Alex", available_minutes=120)
    warnings = Scheduler(owner).detect_conflicts([task_a, task_b])
    assert not any("Time overlap" in w for w in warnings)

def test_same_pet_same_slot_flagged():
    """Two tasks for the same pet in the same morning/evening slot should produce a warning."""
    pet = Pet(name="Mochi", species="dog", age=2)
    task_a = Task(description="Walk", time=30, frequency="morning", pet=pet)
    task_b = Task(description="Grooming", time=20, frequency="morning", pet=pet)
    owner = Owner(name="Alex", available_minutes=120)
    warnings = Scheduler(owner).detect_conflicts([task_a, task_b])
    assert any("Slot conflict" in w for w in warnings)

def test_different_pets_same_slot_not_flagged():
    """Two tasks for different pets in the same morning slot should not conflict."""
    pet_a = Pet(name="Mochi", species="dog", age=2)
    pet_b = Pet(name="Whiskers", species="cat", age=3)
    task_a = Task(description="Walk Mochi", time=30, frequency="morning", pet=pet_a)
    task_b = Task(description="Feed Whiskers", time=5, frequency="morning", pet=pet_b)
    owner = Owner(name="Alex", available_minutes=120)
    warnings = Scheduler(owner).detect_conflicts([task_a, task_b])
    assert not any("Slot conflict" in w for w in warnings)

def test_detect_conflicts_empty_list():
    """detect_conflicts() on an empty list should return no warnings."""
    owner = Owner(name="Alex", available_minutes=120)
    warnings = Scheduler(owner).detect_conflicts([])
    assert warnings == []

def test_tasks_without_start_time_skip_overlap_check():
    """Tasks with start_time=None should not trigger a time-overlap warning."""
    pet = Pet(name="Buddy", species="dog", age=2)
    task_a = Task(description="Walk", time=30, frequency="morning", pet=pet, start_time=None)
    task_b = Task(description="Feed", time=30, frequency="morning", pet=pet, start_time=None)
    owner = Owner(name="Alex", available_minutes=120)
    warnings = Scheduler(owner).detect_conflicts([task_a, task_b])
    assert not any("Time overlap" in w for w in warnings)
