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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
