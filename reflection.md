# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial design consists of five classes. Pet holds the animal's basic info (name, species, age, special needs) and can suggest default tasks based on those attributes. Owner stores the person's name, time availability, and care preferences, and also holds a list of their pets. Task is a lightweight data object representing a single care activity — it stores a title, duration, priority, whether it's time-of-day specific, and whether it's mandatory. Schedule is the output of the planning process — it holds the finalized list of scheduled and skipped tasks and tracks total duration. Finally, Scheduler is the logic engine: it takes an Owner, a Pet, and a list of candidate Tasks, and produces a Schedule by sorting and filtering tasks to fit within the owner's time budget.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, my design changed during implementation. One key change was modifying the Scheduler class to accept a list of pets (pets: list[Pet]) instead of a single pet, and integrating the generation of tasks directly from each pet's get_recommended_tasks() method within build_schedule(). Additionally, I added a pet reference to the Task dataclass to maintain association between tasks and their originating pets.

I made this change because the original design had a missing relationship: the Owner class included a pets list, but the Scheduler only handled one pet at a time, which could lead to incomplete or unfair scheduling for owners with multiple pets. By supporting multiple pets, the system now ensures all pets' tasks are considered collectively under the owner's shared time budget, preventing potential oversights and improving the overall logic for multi-pet households.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The scheduler uses a greedy first-fit algorithm: it iterates through tasks sorted by mandatory status, priority, and duration, and adds each one if it fits within the remaining time budget — never reconsidering a task it already skipped.

This means the schedule is not always optimal. For example, if a 25-minute medium-priority task is skipped because only 20 minutes remain, a 10-minute low-priority task that was added earlier could theoretically have been deferred to make room for it. A true optimal solution would require evaluating all possible combinations (a 0/1 knapsack approach), which grows exponentially with the number of tasks.

The greedy tradeoff is reasonable here because pet care tasks are time-sensitive and predictable in size — a walk is always 30 minutes, feeding is always 5. The owner's daily routine benefits more from a fast, consistent schedule than from a mathematically perfect one that takes longer to compute. The sort order (mandatory first, then high priority, then shortest duration) also mitigates the worst-case outcomes by ensuring the most important tasks are always evaluated first, so what gets skipped tends to be genuinely lower-stakes.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
