---
name: linux-production-deploy
description: Safely build and release Rust or other native server binaries to Linux production. Use this skill whenever a deployment mentions macOS-built artifacts, ELF versus Mach-O, architecture mismatch, systemd restart loops, 502 after release, cross-compilation, remote Linux builds, or publishing a local binary to a Linux server. It enforces artifact and migration preflight checks, Linux-native builds, staged rollback, and fail-closed release behavior.
---

# Linux Production Deploy

Use this workflow for any native binary deployed to a Linux host. A binary that
works on the developer's Mac is not a valid production artifact: macOS produces
Mach-O files, while Linux expects ELF files. Never repair this by changing the
filename, permissions, systemd unit, or migration table.

## Safety contract

- Inspect before mutating anything.
- Do not stop or replace the live service until a Linux-compatible artifact has
  passed local checks and the previous binary is saved for rollback.
- Never edit SQLx's `_sqlx_migrations` table to bypass a checksum mismatch.
- Never edit an already-applied migration. If checksums differ, stop and make a
  compatibility plan.
- If an artifact probe fails, do not copy it to the production binary path.
- Keep secrets out of command output and logs.

## Required release sequence

### 1. Identify the target

Record the production OS, kernel, CPU architecture, service name, binary path,
and deployment user. Verify the expected target explicitly:

```sh
uname -s
uname -m
systemctl status oris.service --no-pager
```

For a normal Linux x86_64 target, the release artifact must report `ELF 64-bit`
and `x86-64`. For ARM64 it must report `ELF 64-bit` and `aarch64`/`ARM aarch64`.

### 2. Probe the artifact before upload

Run the probe on the exact file that would be released:

```sh
file ./target/release/oris-server
```

Accept only an ELF binary matching the production architecture. Reject
`Mach-O`, `PE32`, `ASCII text`, an empty file, or an architecture mismatch.
Also verify it is executable and has the expected service version:

```sh
test -s ./target/release/oris-server
test -x ./target/release/oris-server
./target/release/oris-server --version
```

The probe must be automated in the release script and must run again after
upload on the remote host. The remote probe is authoritative.

### 3. Build on Linux

Preferred order:

1. Build in the same Linux production class (a Linux CI runner or a dedicated
   Linux build host).
2. Build in a pinned Linux container with the repository lockfile.
3. Cross-compile only when the target triple, linker, libc, and runtime
   dependencies are explicitly pinned and the resulting ELF is probed.

For a Linux x86_64 build, a typical native build is:

```sh
cargo build --release --locked --bin oris-server
file target/release/oris-server
```

Do not use a developer macOS `target/release` directory as a release source.
Do not copy an entire local `target` directory to production.

### 4. Run release preflights

Before service replacement, run tests and the repository's migration checksum
preflight. The checksum rule is: every migration already present in the
reference deployment must exist byte-for-byte in the current tree; newly added
migrations are allowed. A mismatch is a release blocker.

```sh
cargo test --workspace
python3 scripts/check-migration-checksums.py \
  --reference-dir /path/to/reference/migrations \
  --current-dir orialis-server/migrations
```

If the production environment enables development device authentication, fail
closed before launch. Production must use real authentication configuration.

### 5. Stage, verify, and switch

Upload to a temporary, versioned path, not directly over the live binary. On
the remote host:

```sh
install -m 0755 ./oris-server /opt/oris/bin/oris-server.<release-id>
file /opt/oris/bin/oris-server.<release-id>
ln -sfn /opt/oris/bin/oris-server.<release-id> /opt/oris/bin/oris-server.next
```

Keep the currently running binary as a rollback target. Switch only after the
remote probe, configuration check, and migration preflight succeed. Then:

```sh
systemctl restart oris.service
systemctl is-active --quiet oris.service
curl --fail --silent --show-error https://orialis.jxcz.top/health
```

Check logs for the first startup window. A service that is merely `activating`
or repeatedly restarting is not healthy.

### 6. Automatic rollback

If the process exits, systemd enters a restart loop, health returns non-2xx, or
the first request fails, immediately restore the saved previous binary and
restart the service. Confirm `active`, health 200, and stable restart count.

Never leave systemd pointing at a known-bad artifact while investigating.

## Failure classification

- `exec format error`, `Mach-O`, or `not an ELF`: wrong build host/artifact;
  rebuild on Linux and repeat both probes.
- SQLx `VersionMismatch`: migration bytes differ from the deployed history;
  restore the previous binary and create a compatibility plan. Do not edit the
  migration table or old migration.
- `active (auto-restart)` or public 502: treat as a failed release; rollback
  first, then inspect logs.
- Linux probe passes but startup fails: inspect libc/linker, environment,
  permissions, database access, and service unit separately; do not assume the
  binary format is the cause.

## Required handoff report

Report these facts, in order:

1. target OS and architecture;
2. local and remote `file` probe results;
3. build command and test result;
4. migration preflight result;
5. release id and saved rollback path;
6. systemd state, health result, and whether rollback was needed.

If any item is unknown, say so and do not claim deployment success.
