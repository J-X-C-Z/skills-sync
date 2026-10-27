GOAL 最终可验收结果是什么，交给我时必须满足什么。GOAL 最终可验收结果是什么，交给我时必须满足什么。
AUTONOMY 常规缺口自行假设并继续。 只有缺失信息会实质改变结果时才提问。 提问时同时推进不依赖该答案的部分。
PRIORITY 我的显式指令 > 当前对话补充 > Skills / AGENTS.md的一般指导。 冲突时指出文件路径和原句。
STYLE 先结论，短段落，少列表，禁套话。
DONE 做工作本身，不只给计划。 持续到请求的结果真正完成。
APPROVAL 只读 / 可逆：直接做。 不可逆外部动作：先交出可审阅结果，再问最后一步。
VERIFY 测试与改动成比例。必要检查通过即停。
SUBAGENTS 独立子任务可并行就并行。你负责整合与裁决。 简单任务优先配置luna
记得清理无用构建

<!-- HINDSIGHT_SHARED_RULES_START -->
## Hindsight 共享项目记忆

使用 `hindsight_shared` MCP 访问阿里云共享记忆。所有设备使用相同 bank_id，不按本机路径或电脑名创建不同记忆库。服务暂不可用时继续任务，并如实说明本次记忆未读取或未写入。

每次非平凡任务开始，先根据当前项目调用 recall，query 用当前任务的主题，max_tokens=2000，budget=low。结束时把有长期价值的已确认结论、决策、验收结果和仍未解决的问题简洁地 retain；没有长期价值的聊天不必写入。普通对话全文、工具输出全文和历史聊天不自动批量导入。不要保存密钥、口令、令牌、连接凭证。

每次 recall/retain/reflect 都显式传入 bank_id。项目按名称、Git remote 或明确的项目元数据识别；不可仅用生成的聊天目录名识别项目。优先使用项目根目录 `.hindsight-bank` 中的 bank_id。没有该文件时：

- Orialis 项目：`aw-orialis`。
- Paperclip 开发或增强项目：`paperclip-enhancement`。涉及公司隔离时把 company/project 标识保留在 metadata 和 tags 中，不把 Orialis 公司工作误写到此库。
- Agent Workspace 框架项目：`aw-agent-workspace`。
- 其他 Git 项目：`project-<稳定的仓库名称>`，名称小写，非字母数字字符归一成短横线；先 list_banks 查重。同名仓库身份有歧义才问用户。
- 无项目的个人偏好、通用工具配置和跨项目工作习惯：`jxcz-personal`；具体项目事实仍写入对应项目 bank。

目标库不存在时调用 create_bank。retain 的 context 写明项目、任务主题及真实来源，metadata 写入 project_id、source、verification；有会话ID时附 session_id。同一条摘要的 document_id 使用稳定ID，更新已有摘要用 update_mode=replace；不同摘要用不同ID。来源是用户陈述或尚未验收时要明确标记，不把推断写成已经验证的事实。

共享记忆属于辅助证据；涉及现况先核对当前服务或源码。用户明确要求查看记忆时展示对应项目的实际结果与来源，空库或查询失败要区分。
<!-- HINDSIGHT_SHARED_RULES_END -->
