# Shared Codex skills

This repository contains custom Codex skills intended to be synchronized across computers. The background sync keeps its working copy at `~/.codex/skills-sync`; a convenience link may be kept under `~/Documents/Codex/skills-sync`.

Each skill should live in its own top-level directory and contain a `SKILL.md` file:

```text
skills-sync/
└── my-skill/
    ├── SKILL.md
    ├── scripts/
    ├── references/
    └── assets/
```

Do not commit API keys, tokens, credentials, caches, logs, or machine-specific settings.

The built-in skills under `~/.codex/skills/.system` are managed separately and should not be copied here.

## Setup on another computer

```bash
git clone <private-repository-url> ~/Documents/Codex/skills-sync
```

Then expose each custom skill to Codex while preserving the built-in `.system` directory:

```bash
for skill_dir in ~/Documents/Codex/skills-sync/*; do
  [ -d "$skill_dir" ] || continue
  [ "$(basename "$skill_dir")" = ".git" ] && continue
  ln -sfn "$skill_dir" "$HOME/.codex/skills/$(basename "$skill_dir")"
done
```

After adding or updating a skill:

```bash
cd ~/Documents/Codex/skills-sync
git pull --ff-only
git add .
git commit -m "Update skills"
git push
```

The macOS background job checks once per day. To synchronize immediately, run:

```bash
~/.codex/sync-installed-skills.sh
```
