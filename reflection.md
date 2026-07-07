# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  - My initial UML design was a bit more spread out than what I ended up with. I mapped out the classes based on the different responsibilities the project needed, like representing pets, representing tasks, building a schedule, and explaining that schedule. That led me to sketch six pieces total: Owner, Pet, Task, Scheduler, DailyPlan, and ScheduleEntry, along with a Priority enum for task ratings.
- What classes did you include, and what responsibilities did you assign to each?
  - Owner held the owner's name and preferences, and could have multiple Pets attached to it. Pet stored basic info like species and kept a list of Task objects tied to that pet. Task was a simple data class representing one care activity, with fields like title, duration, priority, and whether it was flexible or not. Scheduler was where all the actual decision making happened, like sorting tasks by priority and fitting them into the available time. DailyPlan was meant to hold the output of that process, and ScheduleEntry was a small helper meant to pair each task with a start and end time.

**b. Design changes**

- Did your design change during implementation?
  - Yeah, once I went back and reviewed my class skeleton, I caught a couple of structural issues I hadn't noticed while just drawing the UML. The main one was that Scheduler needed to reach an owner's preferences, but there was no path to actually get there from a Pet or Task object. I also noticed available_minutes was awkwardly defined in two places at once.
- If yes, describe at least one change and why you made it.
  - The bigger fix was adding an owner back reference on Pet, since preferences live on Owner but Scheduler only really has access to Pet and Task objects when building a plan. Without that link, there was no way for the scheduling logic to factor in things like preferred walk times. I also removed available_minutes from Scheduler.**init** and kept it only as a parameter on generate_plan(), since having it defined in both places could have caused a mismatch between what the scheduler was initialized with and what got passed in later. Making Scheduler stateless this way means each call to generate_plan() is self contained and easier to test on its own.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  - My scheduler considers three main constraints: available time, task priority, and whether a task is fixed to a specific clock time. Available time acts as a hard budget, once it's used up, nothing else gets scheduled no matter how important it is. Priority determines the order flexible tasks get slotted in, since a busy owner would rather guarantee the high priority stuff happens even if something low priority gets bumped. Fixed time tasks get treated differently from flexible ones, since something like giving meds at a specific time isn't something the scheduler should feel free to move around.
- How did you decide which constraints mattered most?
  - I decided time and fixed commitments mattered most because those are non-negotiable in real life. A pet owner can't stretch their actual number of free minutes, and a vet appointment can't just happen whenever the algorithm feels like it. Priority came second, since it's more of a soft preference that only matters once the hard constraints are already satisfied.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  - One tradeoff my scheduler makes is that it detects scheduling conflicts (two fixed time tasks that overlap) but doesn't automatically resolve them. It just returns a warning message explaining what overlaps and lets the owner decide what to do about it, instead of picking one task to bump or trying to auto-reschedule around the conflict.
- Why is that tradeoff reasonable for this scenario?
  - This is a reasonable tradeoff for this scenario because automatically resolving a conflict would mean the scheduler is making a judgment call it doesn't actually have enough context for. If "Vet drop-off" and "Vet pickup" collide, the algorithm has no way of knowing which one the owner would rather move, or whether the times were even entered correctly. Surfacing the conflict and letting a human make that call keeps the scheduler simple and predictable, and avoids a situation where it silently reschedules something important without the owner realizing it happened.

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
