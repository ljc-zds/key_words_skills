# Discussion Before Creation

The user wants the assistant to discuss ideas first when a skill design is unclear, then execute once the direction is set.

## Ask Before Creating When

- The skill name is missing and no obvious name exists.
- The target path matters: global user skill vs project repo skill.
- The workflow has high-risk actions, business rules, money, legal, account access, or external side effects.
- The user asks for “有什么想法可以先和我讨论”.
- The supporting files are unclear and creating many placeholders would be noisy.

## Do Not Over-Ask When

- The user provides a name and says to follow the recommendation.
- The skill is clearly a personal workflow; use global path.
- The directory structure can be inferred from the supplied template.
- The user asks to execute directly.

## Minimal Question Set

When clarification is needed, ask only what changes the result:

1. Skill name?
2. Global path or project path?
3. What triggers the skill?
4. What should it refuse or escalate?
5. What files should be in `references/` and `templates/`?

## After Agreement

Once the user confirms, create the files immediately. Do not end with another promise to create later.
