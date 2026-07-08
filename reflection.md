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
  - I used Claude code for designing the UML diagrams, being able to understand each relationship between objects and classes. I wanted to feed the AI as much data and context as possible. After each refactoring, I made sure to debug for any errors the AI made and prompted to fix code errors that were hard to detect.
- What kinds of prompts or questions were most helpful?
  - The kinds of prompts and questions that were most helpful were things like "walk me through your logic process on why the classes are structured that way" or something like "What are some ways to improve the UML diagram and how can we best design the classes to be able to implement the required features". The questions that ask the UI for a logical step by step analysis of the code were very important. I had asked questions like "Why can we not implement this feature in another way?" or "Can you run me through a simulation of how the code will work in different use cases" to really dive deep and understand how the AI is thinking.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  - I actually did not accept the AI suggestion as is for the initial UML design. It had some unnecessary classes and made things far too complicated. I wanted to keep the initial UML design simple and easy to understand. It also didn't capture some of the relationships correctly.
- How did you evaluate or verify what the AI suggested?
  - I evaluated each and every class the AI suggested for the initial UML design. I also verified that the relationships for the classes and objects were correct, simply by writing it down and seeing if they made sense. I had to see if enumeration was the correct type for the priority, which I checked through researching the internet (not using AI).

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  - I tested the core behaviors that make up the scheduler, basic task and pet mechanics first (like making sure mark_complete() actually changes a task's status, and that adding a task to a pet increases its task count), then moved into the more algorithmic stuff as I built it out. For sorting, I tested that tasks added out of order actually come back in chronological order, and that tasks with no fixed time don't mess up the ordering by sorting in the wrong spot. For recurring tasks, I tested that completing a daily task creates a new task due exactly one day later, and a weekly one due exactly seven days later, plus I made sure a one-off task doesn't accidentally spawn a copy of itself. For conflict detection, I tested that two tasks at the exact same time get flagged, but also that two tasks that are just back-to-back (one ending right when the other starts) don't get flagged, since that's a real boundary case where it would be easy to get the comparison backwards.
- Why were these tests important?
  - These tests mattered because most of the bugs I ran into while building this weren't in the "obvious" logic, they were in edge cases I wouldn't have caught just by running main.py and eyeballing the output. For example, the back-to-back conflict test specifically checks that my overlap comparison uses a strict less-than instead of less-than-or-equal, which is the kind of off-by-one mistake that's easy to write wrong and easy to not notice unless there's a test forcing you to check it.

**b. Confidence**

- How confident are you that your scheduler works correctly?
  - I'd say I'm fairly confident, maybe a 4 out of 5, that the scheduler works correctly for the behaviors I actually tested. The tests are specific enough that they'd catch a real regression if I broke the date math or the sorting logic later, they're not just checking "does it run without crashing." What brings my confidence down a bit is that I don't have a full end-to-end test that builds a realistic day with a mix of fixed-time tasks, flexible tasks, and a tight time budget all at once, and checks the entire output of generate_plan() together. All my tests check one piece in isolation, so there could still be a bug that only shows up when multiple pieces interact that I just haven't hit yet.
- What edge cases would you test next if you had more time?
  - If I had more time, I'd want to test a pet with zero tasks at all (making sure nothing crashes on an empty list), a task whose duration is longer than the entire available time budget by itself, and what happens if someone marks a recurring task complete when it was never actually attached to a pet. I'd also want to test conflict detection across two different pets combined into one list, not just conflicts within a single pet's tasks, since that's a case I added later and I'm less sure I've stress-tested it as thoroughly as the original single-pet version.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  - I am really satisfied with the whole scheduling output and the way the app comes together in general. I like the fact that I can toggle between pets and see if there are conflicts in the scheduling before I even generate the whole schedule. I really liked learning how much the AI can do with a project like this. I am satisfied with the scope of the tests because they tested the behaviors that I wanted. I am really glad that there were 13 tests made and each one of them passed.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  - If I had another iteration, I'd fix the biggest gaps between what the app promises and what it actually does: preferences is accepted by the scheduler but never used, due_date isn't checked before scheduling a recurring task's next occurrence even though I already wrote is_due() for it, and there's no way to edit or delete a task once it's added (which also means my length-based task IDs would break if I added deletion, since two tasks could end up with the same ID). I'd also want the app to actually persist data between sessions instead of losing everything on refresh, since right now it's just sitting in st.session_state with nothing saved.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  - One big thing I learned is that a lot of my design decisions weren't really about writing code, they were about deciding what to leave out. Cutting DailyPlan and ScheduleEntry down to fit a 4-class limit taught me that a class only earns its place if it actually owns behavior, not just because it represents a "real world thing" like an owner or a schedule. I also learned that working with AI on this project was most useful when I asked it to poke holes in what I'd already built, like when it caught that my Scheduler had available_minutes defined in two conflicting places, or that my UML diagram still showed a dependency on Pet for reading preferences that didn't actually exist in my real code anymore. It was a lot easier to catch that kind of drift between my design and my implementation by asking "does this still match?" instead of assuming my diagram was still accurate just because I hadn't touched it in a while.
