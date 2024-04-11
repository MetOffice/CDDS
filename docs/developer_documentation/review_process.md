!!! warning

    This documentation is currently under construction and may not be up to date.

- The reviewer and reviewee discuss the type of review required.
    - If time is a factor, focus effort on the High Priority items.
    - Agree whether the reviewer can make corrections related to the Low Priority items, e.g., typos or unused imports, directly to the branch.
- If the reviewer feels they need more information after an initial look at the code, they request a pair review with the reviewee.
- The reviewer presents the review to the reviewee (with reasons for priority as necessary), either via the Jira ticket (e.g., if the feedback is minimal), a Confluence page, e-mails, or in person, as appropriate.
- The reviewee assesses the reviewer's recommendations and makes any appropriate changes to the code.
    - Open a new Jira ticket for any low risk issues that do not need to be resolved immediately.
- The reviewee documents the important points from the review about why things were done (or not done) for whatever reasons on the Jira ticket (for future reference).
- The reviewee updates the [Coding Guidelines](coding_guidelines.md) appropriately.

### Review Checklists

#### High Priority

- [ ] Is the code in version control?
- [ ] Does the code work as expected?
- [ ] Does the code manage the risk around availability of resources such as files, databases, mass (assess the risk though first)
- [ ] Does the code check for common errors?
- [ ] Does the code use exceptions appropriately?
- [ ] Are there corresponding unit tests for the code?
- [ ] Can the unit tests be executed?
- [ ] Is there corresponding documentation for the code?
- [ ] Can the documentation be built?
- [ ] Is the documentation easy to understand?

#### Medium Priority

- [ ] Is the code easy to read and understand?
- [ ] Has repetitive code been avoided?
- [ ] Is the code easy to maintain?

#### Low Priority

-  [ ] Does the code comply to the coding standards?
