---
name: weflow-school-notices
description: "Use when the user asks for school-group notices from WeFlow. Read the six saved WeFlow groups locally, filter actionable notices, and summarize concisely."
version: 1.0.0
---

# WeFlow School Notices

Use the local WeFlow HTTP API, never a remote service.

- Base URL: read `WEFLOW_API_URL` (default `http://127.0.0.1:5031`).
- Token: read `WEFLOW_API_TOKEN`; never print it, quote it, or include it in a reply.
- Authenticate with `Authorization: Bearer $WEFLOW_API_TOKEN`.
## 监控范围（课程教学群）

只监控下列**课程/教学群**；这三类不使用：无通知价值的小组群、娱乐群、社群活动群。

- `48157425733@chatroom` — 2026电信二班（班级群，保留）
- `47670028543@chatroom` — 大学物理实验（大物实验二上IJ组）
- `58437908351@chatroom` — 高等数学（高数一·电子信息）
- `44817457327@chatroom` — 学术英语（26秋学术英语周三5-6）
- `58908892273@chatroom` — 体能-大一-周三78
- `48801735564@chatroom` — 26级电路理论
- `49017535383@chatroom` — 习概 周四
- `50445807422@chatroom` — 现代企业制度与公司治理

**明确不监控**（用户指定：小组群没有重要通知）：

- `46125241566@chatroom` — 习概小组
- `50177814488@chatroom` — 现代企业制度与公司治理小组
- `50452607220@chatroom` — 大物实验IJ地下组

非微信平台的课程群（WeFlow 读不到，如需纳入改用 local-message-hub MCP）：
企业微信 `R:130893925649450` 2026年26级程序设计；QQ `1121956022` 2026级 大学物理（理）上-王老师桂老师班级。

- Endpoint: `/api/v1/sessions/{urlencoded_group_id}/messages?limit=5000&since={unix_timestamp}`。
- 返回 `messages[]`，每项 `{sender, accountName, timestamp, type, content, platformMessageId}`；`content` 可能是字符串或对象，先 `json.dumps` 再处理。
- 解析 type：`0` 文本、`1` 图片、`3` 视频、`5` 表情、`25` 引用/卡片文字、`80` 系统消息（`<sysmsg>`，加群/撤回/隐私提示，直接丢弃）、`99` appmsg XML（文件、链接、群公告都在这里）。
- `99` 里的文件消息：文件名在 `<title>`，大小在 `<totallen>`，`<attachid>`/`<aeskey>` 只是 CDN 凭据；群公告在 `<announcement>` 的 `<datadesc>` 里就是公告正文。
- 本 API **只读、不提供附件下载**（`/api/v1/files`、`/export` 均 404，`/api/v1/media/` 只服务已导出的媒体目录）。群里的 pptx/pdf 若用户没在客户端点开过，本地没有文件，只能报“未下载”，不要凭文件名猜内容；需要正文时走消息中枢的 `provider.media()`（见 skill message-hub-chat-analysis）。
- Default to the last 14 days unless the user specifies a period; when the user specifies a period such as 7 days, use it based on each message's publication timestamp.
- Maintain a local cache of fetched messages, pruning each entry individually when its publication timestamp is older than the requested retention window. The cache is for deduplicating fetch/processing work, not for suppressing old notices from the report.
- On each request, combine retained cached messages with newly fetched messages, then produce an integrated current notice summary; do not report only newly fetched messages.
- Keep text messages and relevant structured messages; ignore greetings, holiday wishes, chatter, and media placeholders.
- Prioritize deadlines, class time/place changes, homework, required forms/payments, attendance, exams, materials, and teacher answers.
- Convert timestamps to China Standard Time and state the time range.
- If the API returns 401, the app's `httpApiToken` has rotated: re-derive it from `%APPDATA%\weflow\WeFlow-config.json` → `httpApiToken` (`safe:` + base64 of a Chromium `v10` blob) using the DPAPI key in `%APPDATA%\weflow\Local State` → `os_crypt.encrypted_key`, then update `WEFLOW_API_TOKEN` in the Hermes profile `.env` (never write the token into this file or any reply).
- If the API is unavailable, say so plainly; do not invent notices.
