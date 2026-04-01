from pawpal_system import Pet, Owner, Task, Scheduler

# --- Setup pets ---
pet1 = Pet(name="Mochi", species="dog", age=3, special_needs=["needs extra exercise"])
pet2 = Pet(name="Whiskers", species="cat", age=2, special_needs=["needs grooming"])

# --- Add tasks deliberately out of order (low > medium > high > mandatory) ---
# Mochi's tasks
pet1.tasks.append(Task(description="Brush teeth",         time=10, frequency="daily",   priority="low",    is_mandatory=False, pet=pet1))
pet1.tasks.append(Task(description="Flea treatment",      time=5,  frequency="weekly",  priority="medium", is_mandatory=False, pet=pet1))
pet1.tasks.append(Task(description="Evening playtime",    time=20, frequency="evening", priority="medium", is_mandatory=False, pet=pet1))
pet1.tasks.append(Task(description="Morning walk",        time=30, frequency="morning", priority="high",   is_mandatory=True,  pet=pet1))

# Whiskers' tasks
pet2.tasks.append(Task(description="Cat enrichment toys", time=15, frequency="daily",   priority="low",    is_mandatory=False, pet=pet2))
pet2.tasks.append(Task(description="Litter box cleaning", time=15, frequency="daily",   priority="medium", is_mandatory=False, pet=pet2))
pet2.tasks.append(Task(description="Feed Whiskers",       time=5,  frequency="daily",   priority="high",   is_mandatory=True,  pet=pet2))

# --- Create owner and scheduler ---
owner = Owner(name="Jordan", available_minutes=80, pets=[pet1, pet2])
scheduler = Scheduler(owner)

# --- Show all tasks before any completions ---
print("=" * 55)
print("INITIAL TASKS (added low > medium > high):")
print("=" * 55)
for task in scheduler.retrieve_tasks():
    status = "DONE" if task.completion_status else "pending"
    print(f"  [{status}] {task.description:<28} | {task.frequency:<7} | {task.priority} priority")

# --- Mark a daily task and a weekly task complete ---
# This triggers next_occurrence() to auto-append the next instance
litter_task   = pet2.tasks[1]  # "Litter box cleaning" (daily)
flea_task     = pet1.tasks[1]  # "Flea treatment"      (weekly)

print()
print(f'  Completing: "{litter_task.description}" (daily)')
litter_task.mark_complete()

print(f'  Completing: "{flea_task.description}" (weekly)')
flea_task.mark_complete()

# --- Show all tasks after completions — next occurrences should appear ---
print()
print("=" * 55)
print("TASKS AFTER COMPLETION (next occurrences auto-added):")
print("=" * 55)
for task in scheduler.retrieve_tasks():
    status = "DONE" if task.completion_status else "pending"
    print(f"  [{status}] {task.description:<38} | {task.frequency:<7} | {task.priority} priority")

# --- Filter, sort, and build schedule using only pending tasks ---
all_tasks    = scheduler.retrieve_tasks()
pending      = [t for t in all_tasks if not t.completion_status]
sorted_tasks = scheduler.organize_tasks(pending)

print()
print("=" * 55)
print("SORTED PENDING TASKS (mandatory > priority > duration):")
print("=" * 55)
for task in sorted_tasks:
    print(f"  {task.description:<38} | {task.priority:<6} | mandatory={task.is_mandatory} | {task.time} min")

# Temporarily swap each pet's task list to only pending tasks, then build schedule
for pet in owner.pets:
    pet.tasks = [t for t in pet.tasks if not t.completion_status]

schedule = scheduler.build_schedule()

print()
print("=" * 55)
print("TODAY'S SCHEDULE:")
print("=" * 55)
print(schedule.display())

print()
print("=" * 55)
print("PLAN EXPLANATION:")
print("=" * 55)
print(scheduler.explain_plan(schedule))

# ---------------------------------------------------------------------------
# CONFLICT DETECTION DEMO
# ---------------------------------------------------------------------------
# Build a fresh set of tasks with explicit start_times to trigger both
# conflict types:
#   1. Time-window overlap  -- Mochi's walk and Whiskers' feeding start at
#      the same time (08:00), and their windows overlap
#   2. Same-slot conflict   -- Mochi has TWO tasks tagged "morning"

print()
print("=" * 55)
print("CONFLICT DETECTION DEMO:")
print("=" * 55)

conflict_tasks = [
    # Mochi: morning walk starts 08:00, runs 30 min  (08:00-08:30)
    Task(description="Morning walk",      time=30, frequency="morning", priority="high",
         is_mandatory=True,  pet=pet1, start_time=8*60),
    # Mochi: second morning task -- same slot conflict with Morning walk
    Task(description="Morning grooming",  time=15, frequency="morning", priority="medium",
         is_mandatory=False, pet=pet1, start_time=8*60 + 20),   # 08:20-08:35 (overlaps walk)
    # Whiskers: feeding starts 08:15, runs 5 min  (08:15-08:20) -- overlaps walk window
    Task(description="Feed Whiskers",     time=5,  frequency="daily",   priority="high",
         is_mandatory=True,  pet=pet2, start_time=8*60 + 15),
    # Afternoon task with no overlap -- should produce no warning
    Task(description="Evening playtime",  time=20, frequency="evening", priority="medium",
         is_mandatory=False, pet=pet1, start_time=18*60),
]

print("Tasks in conflict demo (with start times):")
for t in conflict_tasks:
    def fmt(m): return f"{m//60:02d}:{m%60:02d}"
    slot = f"{fmt(t.start_time)}-{fmt(t.start_time + t.time)}" if t.start_time is not None else "no start time"
    print(f"  {t.description:<22} | {t.frequency:<7} | {slot} | pet={t.pet.name}")

print()
warnings = scheduler.detect_conflicts(conflict_tasks)
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")
