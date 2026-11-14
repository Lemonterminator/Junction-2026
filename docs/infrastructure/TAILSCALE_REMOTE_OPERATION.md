# 通过 Tailscale 远程操作机器人工作站

更新：2026-11-14。本文是方案和操作步骤，**尚未执行**：没有改动 tailnet 策略、机器名、
SSH 服务或 Studio 端口。现有事实来自 [SETUP_STATUS](SETUP_STATUS.md)、
[SYSTEM_AUDIT](SYSTEM_AUDIT.md)、[TEAM_CONNECTION_GUIDE](TEAM_CONNECTION_GUIDE.md)、
[DOCKER](DOCKER.md) 和 [执行计划](../plans/PHYSICAL_AI_EXECUTION_PLAN.md) 4.4。
需要队友回答的问题（管理员、5090 环境、现场窗口等）集中在
[交接文档](../../memory/handoffs/2026-11-14-tailscale-and-team-questions.md)。

已验证（一次性，2026-11-14）：一台已加入 tailnet 的操作员笔记本 `tailscale ping 100.76.18.70`
先经 DERP 后转直连（8 ms），netcheck 显示 UDP/IPv4/IPv6 可用；TCP 22 和 7860 可达，443 不通；
tailnet 里目前只有两台设备，没有 5090。

## 1. 先说清楚“远程操控”指什么

SO-101 的遥操作是 **leader 臂 → follower 臂** 的串口闭环。Studio 中两条臂都是
backend 所在主机（Intel 工作站）上的 USB 设备（`ttyACM0` / `ttyACM1`），闭环在该主机
本地运行，**不经过网络**。因此本方案分三类流量：

| 类型 | 走 tailnet? | 说明 |
| --- | --- | --- |
| leader→follower 遥操作闭环 | 否 | 两臂都插在 Intel 上，现场有人手持 leader。延迟不受网络影响。 |
| Studio 界面（配置、标定、录制开始/停止、相机预览、发起训练、运行策略） | 是 | 全部经 HTTP 端口 7860；相机预览是同一端口上的 WebSocket JPEG 帧（`backend/src/api/camera.py`）。 |
| 本仓库的实时页面（`sorter-live-demo` 默认 8090，`sorter-alignment` 默认 8091） | 是 | 绑定 Tailscale IP；浏览器按帧拉取 `/frame.jpg`（见 `webview.py`），不是推送的 MJPEG 流。同一时刻只有一个进程能开 D415。页面带 POST 操作但无鉴权，所以同样只对操作员开放。 |
| SSH / VS Code / tmux / Claude | 是 | 端口 22，现有 `junction-ssh.service` 只监听 `100.76.18.70`。 |
| Studio → 5090 远程 trainer | 是 | Studio 通过 SSH 连接 trainer，上传数据快照、拉回模型；吞吐敏感，延迟不敏感。 |

**不推荐**把 leader 放在远端、follower 放在现场（例如 USB over IP 或自写网络桥）。
Studio 不支持这种拓扑；网络抖动会直接变成机械臂抖动，且远端操作者看不到也够不到
急停。远程同学的角色是“监控和发起”，动作由现场负责人在场时执行。

## 2. tailnet 与设备命名

在 Tailscale 管理后台（Machines）把机器改成短名，MagicDNS 名随之变化：

| 机器 | 建议名 | 标签 | 说明 |
| --- | --- | --- | --- |
| Intel 工作站（现 `intel-hp-omnibook-ultra-laptop-14t-kd000`，`100.76.18.70`） | `junction-intel` | `tag:robot` | Studio backend、两条臂、三台相机、OpenVINO 部署 |
| 5090 训练机 | `junction-5090` | `tag:trainer` | Studio SSH trainer |
| 队员笔记本 | 保持个人名 | 无（按用户身份） | 各自登录同一 tailnet |

注意：

- 改名后 MagicDNS 名变为 `junction-intel.taild8fece.ts.net`；现有 SSH 配置用 IP，不受影响，
  但 VS Code/书签中写了旧长名的要改。Tailscale IP 不会因改名变化。
- 打上标签后设备归属从个人变为标签，**默认不再有 key 过期**，适合无人值守的机器；
  但原来基于个人身份的策略规则对它不再生效，必须先写好第 3 节的策略再打标签。
- 5090 若在 Windows + WSL2 上：Studio SSH trainer 需要 Ubuntu SSH 主机（Docker + GPU）。
  建议在 WSL2 发行版内单独安装 Tailscale 和 `openssh-server`，作为独立节点 `junction-5090`；
  Windows 侧的 Tailscale 不会把 22 端口转进 WSL。此路径未验证，按执行计划 4.4 的连接
  排查预算处理。

## 3. 访问策略（ACL / grants）

Studio 没有登录鉴权：**能访问 7860 的人就能让机械臂动**。所以 7860 只开放给操作员组，
开发者组只开 SSH。下面是策略草案（HuJSON，邮箱替换为真实账号；改策略前在管理后台
“Preview rules” 中核对）：

```jsonc
{
  "groups": {
    // 能操作 Studio（标定、录制、运行策略）的人
    "group:operators": ["owner@example.com", "field-lead@example.com"],
    // 只需要 SSH/开发的人
    "group:devs": ["owner@example.com", "dev-a@example.com", "dev-b@example.com"]
  },
  "tagOwners": {
    "tag:robot":   ["autogroup:admin"],
    "tag:trainer": ["autogroup:admin"]
  },
  "grants": [
    // 操作员：SSH + Studio（7860 直连或 443 tailscale serve）
    {"src": ["group:operators"], "dst": ["tag:robot"],   "ip": ["tcp:22", "tcp:443", "tcp:7860", "tcp:8090", "tcp:8091"]},
    // 开发者：仅 SSH；需要 Studio 时用 ssh -L 自己转发，也受 SSH 账户约束
    {"src": ["group:devs"],      "dst": ["tag:robot"],   "ip": ["tcp:22"]},
    // 5090 只需管理员/训练负责人 SSH
    {"src": ["group:operators"], "dst": ["tag:trainer"], "ip": ["tcp:22"]},
    // Studio backend 主动 SSH 到 trainer（上传快照、拉回模型）
    {"src": ["tag:robot"],       "dst": ["tag:trainer"], "ip": ["tcp:22"]}
  ],
  "tests": [
    {"src": "dev-a@example.com", "accept": ["tag:robot:22"], "deny": ["tag:robot:7860"]},
    {"src": "tag:robot", "accept": ["tag:trainer:22"]}
  ]
}
```

- 不需要 trainer → robot 方向的规则；tailnet 内未被允许的连接默认拒绝。
- 若 tailnet 仍是默认的“全部允许”策略，替换前先确认自己的账号在 `group:operators` 中，
  并保留一个现场控制台（显示器 + 键盘）以防把自己锁在外面。
- 不使用 **Tailscale Funnel**：它会把服务暴露到公网。

## 4. SSH

保持现有 OpenSSH（`junction-ssh.service` 绑定 `100.76.18.70:22`）和个人 ed25519 密钥流程，
见 [TEAM_CONNECTION_GUIDE](TEAM_CONNECTION_GUIDE.md)。改名后可把 `HostName` 换成
`junction-intel`（MagicDNS），IP 写法也继续可用。

可选：Tailscale SSH（`tailscale set --ssh`）能省去分发公钥，但它会接管 tailnet 地址上的
22 端口，与现有 `junction-ssh.service` 冲突，且需要额外的 `"ssh"` 策略段。比赛期间不建议
切换，避免改动已验证的登录路径。

待办：端口 2222 的临时监听仍在，确认无用后由管理员停止；`junction-ssh.service` 的重启
行为未测试，现场开机后先 `ssh junction-intel` 验证一次。

## 5. Studio 界面和相机预览如何走 tailnet

**当前风险**：工作站从 `~/junction` 里子模块的 compose（`external/physical-ai-studio/application/docker`，
项目名 `docker`，见 [DECISIONS](../../memory/DECISIONS.md)）启动 Studio。该文件的端口映射为
`${PORT:-7860}:${PORT:-7860}`、`HOST=0.0.0.0`，即 7860 **发布在所有网卡**（已读文件确认；未检查
正在运行的容器），场馆 Wi-Fi 上任何人都可能打开 Studio 并操作机械臂。UFW 未启用，tailnet 策略管不到
局域网接口。**注意 Docker 发布的端口通常绕过 UFW 规则**，所以只启用 UFW 不能解决问题，
要改端口绑定。不要直接改子模块里的文件（它是固定版本的上游代码）：用一个放在本仓库的
`compose` 覆盖文件把 `ports` 改成 `127.0.0.1:7860:7860`，再用 `-f` 叠加启动（覆盖文件待写、待测）。
建议三选一（按推荐顺序）：

1. **绑定 loopback + `tailscale serve`（推荐）**：改为本仓库的 compose（已是
   `127.0.0.1:${STUDIO_PORT}:7860`），或在上游 compose 的 `ports` 写 `127.0.0.1:7860:7860`，
   然后在工作站执行
   ```bash
   sudo tailscale serve --bg --https=443 http://127.0.0.1:7860
   tailscale serve status
   ```
   操作员打开 `https://junction-intel.taild8fece.ts.net/`。需要在管理后台启用 HTTPS 证书；
   serve 会代理 WebSocket，相机预览应可工作（未实测）。
2. **只绑定 Tailscale 地址**：`ports: ["100.76.18.70:7860:7860"]`，访问
   `http://junction-intel:7860`。缺点是开机时 tailscaled 必须先就绪，否则容器启动失败。
3. **每人 SSH 转发**：`ssh -L 7860:127.0.0.1:7860 junction-intel`，打开
   `http://127.0.0.1:7860`。最保守，适合开发者；但多人同时打开同一 Studio 仍会争用同一
   组设备。

改端口映射需要 `docker compose up -d --force-recreate`，会中断正在进行的录制，并且设备
必须在容器启动前插好（见 SETUP_STATUS）。选一个没有录制的时间段，由现场负责人执行。

多人同时打开 Studio 只读查看可以，但同一时刻只能有一个人发起标定/录制/策略运行，
在团队频道里口头“占用/释放”。D415 只能被一个进程打开：远程预览 `sorter-live-demo`
前先确认 Studio 没在用该相机。

## 6. 延迟、带宽与连通性检查

在操作员笔记本上：

```bash
tailscale status                 # 看到 junction-intel / junction-5090 在线
tailscale ping junction-intel    # "via <IP>:<port>" 为直连；"via DERP(xxx)" 为中继
tailscale netcheck               # UDP 是否可用、最近的 DERP 区域
```

- 场馆 Wi-Fi 常有客户端隔离或封 UDP，会退回 DERP 中继：延迟增加、吞吐受限。只影响
  界面和相机预览，不影响 leader→follower 闭环。
- 相机预览是每台相机一路 JPEG 流。3 台 640×480@30 同时预览在中继上可能卡顿（未测，
  带宽取决于 JPEG 大小）；远程时只打开需要的那一路。录制在工作站本地写盘，预览卡顿
  不影响数据，但录制前在本地屏幕确认画面。
- 延迟测量遵守执行计划第 3 节：跨主机不要直接相减单调时钟；演示中的部署延迟只在
  Intel 本机测量，与网络无关。
- 5090 训练：数据快照上传和模型回传是大文件，中继会明显变慢。先用微型数据跑一次
  完整任务链（执行计划 W0.3），记录耗时。

## 7. 安全规则

- 遵守 `AGENTS.md`：任何臂动作（identify、遥操作、策略运行、脚本动作）只在用户本次
  明确要求时执行；过载等错误立即停止并报告，不自动重试。
- **远程发起的任何动作，现场必须有人在机械臂旁，手能够到电源/急停**，并通过语音或
  消息确认“可以动”。远程操作员看到的画面有延迟，不能作为安全依据。
- 7860 只对 `group:operators` 开放；不启用 Funnel；不把 Studio 端口暴露在场馆局域网。
- Studio 设置卷中可能有个人 token（HF 等），不要把 `studio-storage` 卷或截图分享到 tailnet 外。
- 5090 trainer 的 SSH 用户若按上游文档配置 `NOPASSWD: ALL`，等同 root；使用专用账号，
  比赛结束后撤销 sudoers 文件和 `tag:robot → tag:trainer` 规则。
- 比赛结束后：移除临时队员账号/共享节点，撤销 tailnet 邀请，删除授权密钥。

## 8. 现场断网的回退方案

演示主链路（相机 → Anomalib → 决策 → 策略 → follower，OpenVINO 在 Intel 上）全部在
工作站本地运行，**演示本身不依赖 tailnet 或外网**。按故障程度回退：

1. **外网断、局域网仍在**：已建立的 Tailscale 直连通常能继续工作一段时间，但新设备
   无法加入、key/策略无法更新（未在现场验证）。不要在这时改策略或重新登录。
2. **tailnet 不通**：在工作站本机显示器打开 `http://127.0.0.1:7860` 操作 Studio；
   遥操作和录制照常进行。注意 `junction-ssh.service` 只绑定 Tailscale 地址，此时局域网
   SSH 不可用，所以**工作站要常备显示器、键盘、鼠标**。
3. **需要第二台电脑**：用自带的旅行路由器或手机热点组一个小局域网（或网线直连），
   用第 5 节方案 3 的 SSH 转发需要 SSH 监听局域网地址；如需此路径，提前由管理员
   增加一个仅限该热点网段的监听并测试，否则只用本机屏幕。
4. **5090 不可达**：训练提前完成，模型在比赛前导出到工作站；现场不排训练任务。
   紧急情况下按执行计划 4.4 切换到已获准的 Studio Modal 路径（同样需要外网）。
5. **提前离线准备**：Studio 镜像已构建，HF 模型/数据已缓存到本地卷，OpenVINO 模型
   已导出，`pip/uv` 依赖已安装；演示前拔网跑一遍完整闭环，确认没有隐藏的网络依赖。

## 9. 执行顺序（建议）

1. 管理员在后台写入第 3 节策略（先 Preview），保留现场控制台。
2. 给 Intel 打 `tag:robot` 并改名 `junction-intel`；5090 加入 tailnet，打 `tag:trainer`，改名。
3. 每位操作员 `tailscale ping junction-intel`，`ssh junction-intel`，记录直连/中继。
4. 现场负责人在无录制时把 Studio 改为 loopback + `tailscale serve`，从远程笔记本打开
   并确认三路相机预览，记录卡顿情况。
5. 在 Studio Training Targets 注册 `junction-5090`（SSH），跑微型训练任务验证回传。
6. 拔掉外网，在本机屏幕跑一遍“标定 → 遥操作 → 录制 → 部署推理”，确认回退路径可用。

每一步的结果（通过/失败、直连或中继、耗时）记入 `memory/STATUS.md`，未执行的步骤保持
“未验证”。
