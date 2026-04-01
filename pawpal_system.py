from dataclasses import dataclass, field
from itertools import combinations
from typing import Optional, List


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: list[str] = field(default_factory=list)
    tasks: list['Task'] = field(default_factory=list)

    def get_recommended_tasks(self) -> List['Task']:
        """Return a default list of Tasks based on species, age, and special needs."""
        if not self.tasks:  # Only generate if not already done
            # Basic tasks based on species
            if self.species.lower() == "dog":
                self.tasks.append(Task("Walk the dog", 30, "morning", False, "high", True, self))
                self.tasks.append(Task("Feed the dog", 10, "daily", False, "high", True, self))
            elif self.species.lower() == "cat":
                self.tasks.append(Task("Feed the cat", 5, "daily", False, "high", True, self))
                self.tasks.append(Task("Clean litter box", 15, "evening", False, "medium", False, self))
            # Add tasks for special needs
            for need in self.special_needs:
                if "exercise" in need.lower():
                    self.tasks.append(Task(f"Extra exercise for {need}", 20, "daily", False, "medium", False, self))
                elif "medical" in need.lower():
                    self.tasks.append(Task(f"Medical care for {need}", 15, "daily", False, "high", True, self))
        return self.tasks


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def get_available_time(self) -> int:
        """Return the number of minutes the owner has available today."""
        return self.available_minutes

    def get_all_tasks(self) -> List['Task']:
        """Collect and return all tasks from all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_recommended_tasks())
        return all_tasks


@dataclass
class Task:
    description: str
    time: int  # duration in minutes
    frequency: str  # e.g., "daily", "morning", "evening"
    completion_status: bool = False
    priority: str = "medium"  # "low" | "medium" | "high"
    is_mandatory: bool = False
    pet: Optional['Pet'] = None
    start_time: Optional[int] = None  # minutes since midnight, e.g. 480 = 8:00 AM

    def mark_complete(self) -> None:
        """Mark this task as completed and schedule the next occurrence for recurring tasks."""
        self.completion_status = True
        next_task = self.next_occurrence()
        if next_task and self.pet:
            self.pet.tasks.append(next_task)

    def next_occurrence(self) -> Optional['Task']:
        """Return a fresh Task instance for the next occurrence, or None if not recurring."""
        if self.frequency == "daily":
            label = "tomorrow"
        elif self.frequency == "weekly":
            label = "next week"
        else:
            return None
        return Task(
            description=f"{self.description} ({label})",
            time=self.time,
            frequency=self.frequency,
            completion_status=False,
            priority=self.priority,
            is_mandatory=self.is_mandatory,
            pet=self.pet,
        )

    def priority_score(self) -> int:
        """Convert priority string to a numeric score (high=3, medium=2, low=1)."""
        scores = {"high": 3, "medium": 2, "low": 1}
        return scores.get(self.priority.lower(), 2)


class Schedule:
    def __init__(self, owner: Owner, pets: list[Pet]):
        self.owner = owner
        self.pets = pets
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.total_duration: int = 0

    def add_task(self, task: Task) -> None:
        """Add a task to the schedule and update total_duration."""
        self.scheduled_tasks.append(task)
        self.total_duration += task.time

    def is_over_budget(self, available_minutes: int) -> bool:
        """Return True if total_duration exceeds available_minutes."""
        return self.total_duration > available_minutes

    def display(self) -> str:
        """Return a human-readable summary of the scheduled and skipped tasks."""
        lines = [f"Schedule for {self.owner.name} with {len(self.pets)} pet(s):"]
        lines.append(f"Scheduled tasks ({self.total_duration} min):")
        for task in self.scheduled_tasks:
            pet_name = task.pet.name if task.pet else "Unknown"
            lines.append(f"  - {task.description} ({task.time} min, {task.frequency}) for {pet_name}")
        lines.append("Skipped tasks:")
        for task in self.skipped_tasks:
            pet_name = task.pet.name if task.pet else "Unknown"
            lines.append(f"  - {task.description} ({task.time} min, {task.frequency}) for {pet_name}")
        return "\n".join(lines)


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def retrieve_tasks(self) -> List['Task']:
        """Retrieve all tasks from the owner's pets."""
        return self.owner.get_all_tasks()

    def organize_tasks(self, tasks: List['Task']) -> List['Task']:
        """Organize tasks by sorting them based on priority and mandatory status."""
        return sorted(tasks, key=lambda t: (not t.is_mandatory, -t.priority_score(), t.time))

    def build_schedule(self) -> Schedule:
        """Build a schedule by organizing tasks and fitting them within the owner's time budget."""
        tasks = self.retrieve_tasks()
        organized_tasks = self.organize_tasks(tasks)
        schedule = Schedule(self.owner, self.owner.pets)
        available = self.owner.get_available_time()
        for task in organized_tasks:
            if schedule.total_duration + task.time <= available:
                schedule.add_task(task)
            else:
                schedule.skipped_tasks.append(task)
        return schedule

    def sort_by_time(self, tasks: List['Task']) -> List['Task']:
        """Return tasks sorted by their time (duration in minutes), ascending."""
        return sorted(tasks, key=lambda t: f"{t.time // 60:02d}:{t.time % 60:02d}")

    def detect_conflicts(self, tasks: List['Task']) -> List[str]:
        """Return warning strings for overlapping time windows or same-slot same-pet conflicts."""
        warnings = []

        def fmt(minutes: int) -> str:
            return f"{minutes // 60:02d}:{minutes % 60:02d}"

        # Check 1: time-window overlap for any two tasks that both have a start_time
        timed = [t for t in tasks if t.start_time is not None]
        for a, b in combinations(timed, 2):
            if a.start_time < b.start_time + b.time and b.start_time < a.start_time + a.time:
                a_pet = a.pet.name if a.pet else "Unknown"
                b_pet = b.pet.name if b.pet else "Unknown"
                warnings.append(
                    f"WARNING: Time overlap -- '{a.description}' ({a_pet}, "
                    f"{fmt(a.start_time)}-{fmt(a.start_time + a.time)}) conflicts with "
                    f"'{b.description}' ({b_pet}, "
                    f"{fmt(b.start_time)}-{fmt(b.start_time + b.time)})"
                )

        # Check 2: same pet, same frequency slot (morning/evening) -- can't run simultaneously
        slots = ("morning", "evening")
        for a, b in combinations(tasks, 2):
            if (a.pet and b.pet and a.pet is b.pet
                    and a.frequency == b.frequency
                    and a.frequency in slots):
                warnings.append(
                    f"WARNING: Slot conflict -- '{a.description}' and '{b.description}' "
                    f"are both scheduled {a.frequency} for {a.pet.name}"
                )

        return warnings

    def explain_plan(self, schedule: Schedule) -> str:
        """Return a plain-English explanation of why each task was included or skipped."""
        explanations = []
        for task in schedule.scheduled_tasks:
            explanations.append(f"Included '{task.description}' because it fits within time budget and has {'mandatory' if task.is_mandatory else f'{task.priority} priority'}.")
        for task in schedule.skipped_tasks:
            explanations.append(f"Skipped '{task.description}' because it would exceed the {schedule.owner.available_minutes} minute time budget.")
        return "\n".join(explanations)