# agent-skills

A collection of agent skills following the open [Agent Skills](https://github.com/anthropics/skills) standard — portable across Claude, Cursor, and any compatible AI agent.

Each skill is a self-contained folder with a `SKILL.md` file and optional `references/` for progressive disclosure. Agents load the frontmatter up front and pull the body + references only when the skill is relevant to the user's task.

## Skills

| Skill | Tags | Description |
|---|---|---|
| [laravel-service-modules](./skills/laravel-service-modules) | `laravel` `php` | Scaffolds, reviews, or refactors external API integrations in Laravel using the Service Module pattern (Repository + Interface + Provider + Facade + DTO + Exception) |

## Install

Install any skill from this repo using the [skills.sh](https://skills.sh) CLI:

```bash
npx skills add shreifelagamy/agent-skills
```

This registers every skill in the repo with your local agent (Claude Code, Cursor, etc.). Run from your project root or home directory — whichever matches your agent's skill discovery path.

See [skills.sh/docs](https://skills.sh/docs) for CLI options.

## Structure

```
agent-skills/
├── README.md              ← you are here
├── LICENSE                ← MIT
└── skills/
    └── <skill-name>/
        ├── SKILL.md       ← frontmatter + core instructions
        └── references/    ← progressive-disclosure content
```

## Contributing

Issues and PRs welcome. When adding a new skill:

- Folder name must be kebab-case and match the `name:` field in frontmatter
- `SKILL.md` must include `name`, `description`, and `tags` (`laravel` or `php` triggers auto-import to [skills.laravel.cloud](https://skills.laravel.cloud))
- Keep `SKILL.md` lean — move heavy content into `references/`
- No `README.md` inside skill folders (Agent Skills spec)

See the [Anthropic Agent Skills guide](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) for best practices.

## License

MIT — see [LICENSE](./LICENSE)
