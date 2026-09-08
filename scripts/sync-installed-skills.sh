#!/bin/zsh

set -u

SOURCE_DIR="${HOME}/.codex/skills"
REPO_DIR="${HOME}/.codex/skills-sync"
LOG_FILE="${TMPDIR:-/tmp}/codex-skills-sync.log"
LOCK_DIR="${TMPDIR:-/tmp}/codex-skills-sync.lock"

log() {
  print -r -- "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG_FILE"
}

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

if [[ ! -d "$SOURCE_DIR" || ! -d "$REPO_DIR/.git" ]]; then
  log "Skipped: source or repository is unavailable"
  exit 0
fi

cd "$REPO_DIR" || exit 1

if ! /usr/bin/git pull --ff-only origin main >> "$LOG_FILE" 2>&1; then
  log "Skipped: git pull failed; resolve repository state manually"
  exit 1
fi

# Copy locally installed skills into the repository. Keep built-in .system out.
for skill_dir in "$SOURCE_DIR"/*(N/); do
  skill_name="${skill_dir:t}"
  [[ "$skill_name" == ".system" ]] && continue
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  /usr/bin/rsync -a --exclude '.DS_Store' "$skill_dir/" "$REPO_DIR/$skill_name/"
done

/usr/bin/git add -A
if ! /usr/bin/git diff --cached --quiet; then
  /usr/bin/git commit -m "Sync installed Codex skills" >> "$LOG_FILE" 2>&1 || exit 1
  /usr/bin/git push origin main >> "$LOG_FILE" 2>&1 || {
    log "Push failed; local commit is preserved"
    exit 1
  }
fi

# Pull repository-only skills down to this computer.
for skill_dir in "$REPO_DIR"/*(N/); do
  skill_name="${skill_dir:t}"
  [[ "$skill_name" == ".git" ]] && continue
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  /usr/bin/rsync -a --exclude '.DS_Store' "$skill_dir/" "$SOURCE_DIR/$skill_name/"
done

log "Sync complete"
