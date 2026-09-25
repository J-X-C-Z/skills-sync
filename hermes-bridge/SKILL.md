---
name: hermes-bridge
description: 向 Hermes Agent 投递消息或读取 Codex⇄Hermes 双向信箱。当 Codex 需要把结果、状态、文件路径回传给 Hermes，或需要查看 Hermes 写来的消息时使用。
version: 1.0.0
author: codex-hermes-mcp
license: MIT
---

# hermes-bridge（Codex → Hermes）

用本机信箱与 Hermes 双向互通，无需控制对方屏幕。

## 投递到 Hermes

```bash
node /Users/jxcz/XiaomiMiMoProjects/2026-09-23/codex-hermes-mcp/bin/ch-inbox.mjs \
  send "diff 已整理，见 /tmp/pr.diff" --to hermes --subject review
```

- `--to hermes` 目标侧  
- `--subject` / `--session` / `--reply-to` 可选  
- stdin：`echo "..." | ... ch-inbox send - --to hermes`  

成功输出：`{ "ok": true, "id": "...", "side": "to_hermes", "file": "..." }`。

## 查看 / 领取本侧信箱

```bash
node .../bin/ch-inbox.mjs list --side to_codex     # Hermes 写给 Codex
node .../bin/ch-inbox.mjs claim --side to_codex    # 领取并移入 processed/
node .../bin/ch-inbox.mjs status
```

默认根目录：`~/.codex_hermes_mailbox`（`CODEX_HERMES_MAILBOX` 可覆盖）。

## 说明

- 只做信箱投递；要 Hermes 立刻处理请在 body 写清上下文与下一步。  
- 不要把密钥写进消息正文。  
