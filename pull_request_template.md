# Pull Request

## Description

A summary of the pull request (PR) and the issue it resolves. Please include the following:

* A link to the relevant issue and/or ClubHouse card
* A code "walk-through" in bullet points

## Checklists

### Basic

- [ ] Did you write tests for the code in this PR?
- [ ] Did you document your changes in the README and/or in docstrings (as needed)?

### Security

- [ ] Authorization has been implemented across these changes
- [ ] Injection has been prevented (parameterized queries, no eval or system calls)
- [ ] Any web UI is escaping output (to prevent XSS)
- [ ] Sensitive data has been identified and is being protected properly

## Notes for the Reviewer

A precise explanation of what the PR reviewer needs to evaluate. This might be:

* a low-level code review of certain functions
* a high-level assessment of strategy or architecture
* a confirmation that the code behaves as expected on another machine
