# AI 共享记忆

本项目使用 Git 中的 Markdown 作为共享上下文。入口是根目录 `AGENTS.md`（Codex）
和 `CLAUDE.md`（Claude）；内容集中于 [memory/](../../memory/README.md)。
Codex 的项目指令发现机制见 [OpenAI 官方文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。
其他 AI 可以手动要求其读取这些入口。Claude 入口在本项目中已准备，尚未启动 Claude 会话验证。

每次新会话可使用：

```text
请读取 AGENTS.md、memory/PROJECT.md、memory/STATUS.md 和 memory/DECISIONS.md，
按当前工作树和相关交接记录继续任务。结束时更新状态，记录实际检查和未验证事项。
```

这能让不同账号和工具读取相同的项目事实；它不会自动同步聊天历史。共享发生在
提交、合并和 pull 之后。多人同时工作时新增独立的交接文件，提交前重新查看状态，
处理 memory 文件的实际冲突。不要整份覆盖队友新增的事实。

项目根目录是内层 `Junction-2026/`。当前 Codex 工作区包含外层目录；新会话请将此
Git 根目录作为工作目录，或显式要求读取内层 `AGENTS.md`，以确保加载项目入口。

长期事实放 PROJECT；进度和验证放 STATUS；决策放 DECISIONS；具体工作经过放 handoffs。
历史硬件审计是带时间的证据，不能自动当成当前机器状态。密码、令牌、SSH 私钥、
私有账号缓存和含敏感信息的聊天记录不进入这些文件。
