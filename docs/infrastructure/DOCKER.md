# Docker 开发环境

本项目从 `external/physical-ai-studio` 的固定提交构建 Studio，复用上游 Dockerfile；
镜像中包含 Python 3.13 和已构建 UI。CPU 默认环境不依赖相机或机械臂。
Anomalib 2.7.0 位于独立容器，避免与 Studio 的 PyTorch 环境冲突。

## 1. 初始化（在 Git 根目录）

```bash
git submodule update --init --recursive
cp .env.example .env
cp docker/secrets.env.example docker/secrets.env
```

PowerShell 对应使用 `Copy-Item .env.example .env` 和
`Copy-Item docker/secrets.env.example docker/secrets.env`（首次创建时执行）。
每个人修改自己的 `.env`：选择独立的 `COMPOSE_PROJECT_NAME`、可用 `STUDIO_PORT`；
Linux 用户填写 `id -u` / `id -g` 对应的 `APP_UID` / `APP_GID`。
这些文件已忽略；只填写个人凭证，不共享令牌。

Docker Engine 需要可用的 Linux 容器后端；Compose 需要支持 `additional_contexts` 和
可选 `env_file`（建议 v2.24+）。当前 Windows 检查结果：CLI/Compose 已安装，启动
Docker Desktop 后 Linux 引擎仍不可用，`wsl --status` 提示未安装 WSL。需要先完成
[Docker Desktop WSL 后端前置条件](https://docs.docker.com/desktop/features/wsl/)。
本次没有安装 WSL、修改 Windows 可选组件或重启机器。

## 2. CPU Studio

```bash
docker compose config --quiet
docker compose build studio
docker compose up -d --wait studio
docker compose ps
```

打开 <http://127.0.0.1:7860>。这是容器中同时提供 UI/API 的端口；原生开发的 UI 3000
端口不适用于本配置。首次构建包含模型依赖与 FFmpeg 编译，可能耗时较长。
构建需要访问 GitHub、镜像仓库和包仓库；成功解析配置不等于构建或运行成功。
容器直接调用上游安装的 `physicalai-studio serve`，避免 Windows 检出 `run.sh` 时的
CRLF 问题；未修改上游源码。

设置 Hugging Face token、Modal token 到 `docker/secrets.env`，或按上游支持的设置
页面配置 HF。编辑环境变量后通过 `docker compose up -d --force-recreate studio`
重新创建服务使其生效。在 UI 配置 Modal 并启动训练前确认个人额度与费用。
不自动启动训练任务。

## 3. 独立 Anomalib 工作区

```bash
docker compose --profile tools build anomalib
docker compose --profile tools run --rm anomalib python -c "from importlib.metadata import version; import openvino, torch; print(version('anomalib'), torch.__version__, openvino.Core().available_devices)"
docker compose --profile tools run --rm anomalib bash
```

仓库挂载到 `/workspace`。训练图像放 `data/`，导出和指标放 `artifacts/`（均忽略）。
创建文件归宿主 UID/GID 所有；Windows 使用默认值即可。该镜像安装 CPU PyTorch，
列出的 OpenVINO 设备取决于实际挂载和运行时；不代表已有训练/检测应用或闭环服务。
本次仅固定 Anomalib 顶层版本；传递依赖未完全锁定，首次成功构建后再保存经验证的锁。
Intel GPU 上的 Anomalib 训练需独立验证，不复用 Studio 环境安装 Anomalib。

## 4. Intel 工作站（原生 Linux）

先确认设备与使用权：`ls -l /dev/dri /dev/accel /dev/video* /dev/ttyACM*`，
对选定设备运行 `stat -c '%g' /实际/设备路径` 获取数字 GID。
填写 `.env` 中的设备变量；渲染节点存在不等于驱动和推理可用。

```bash
docker compose -f compose.yaml -f compose.intel.yaml config --quiet
docker compose -f compose.yaml -f compose.intel.yaml build studio
docker compose -f compose.yaml -f compose.intel.yaml up -d --wait studio
```

该 overlay 切换到上游 XPU 构建目标并映射指定 render node。需要 NPU 时显式追加
`-f compose.npu.yaml`，填写 `NPU_DEVICE` / `NPU_GID`；它只增加设备映射，
不安装主机驱动、不保证容器具有所需 NPU 用户态运行时，也不保证策略可在 NPU 上编译。
先检查 `openvino.Core().available_devices`，再对实际导出模型验证。

确定相机和机械臂独占使用安排后，再追加 `-f compose.robot.yaml`；需要明确
`CAMERA_DEVICE`、`LEADER_DEVICE`、`FOLLOWER_DEVICE` 及数字 GID。额外相机写入
被忽略的 `compose.local.yaml`，并在每次命令中显式 `-f` 加载。RealSense 可能还需
libusb 设备映射；本配置没有默认暴露全部 USB，也没有假定 `/dev/video0` 可用。

所有 build/up/exec/logs/down 命令使用同一组 `-f` 参数和 Compose 项目名；否则可能
将 XPU 服务重建回 CPU。Compose 只映射权限，不解决机器人校准、急停或设备争用。

## 5. 持久化和协作

Studio 数据库、设置、模型保存在 `studio-storage`，缓存和校准在 `studio-cache`；
实际卷名由 Compose 项目名隔离。设置可能含个人 token，卷也不应跨账号共享。
Anomalib 缓存在独立卷。`docker compose down` 保留数据；`down -v` 会删除卷中数据。
共享集成实例的负责人尚未指定，当前配置默认每人一个实例。

服务仅发布到宿主 loopback。远程开发使用 SSH 转发，例如
`ssh -L 7860:127.0.0.1:7860 junction-intel`（按个人 SSH 配置和端口调整）。
未向远端工作站部署。日志与检查命令：

```bash
docker compose logs --tail 100 studio
docker compose exec studio python -c "import openvino as ov; print(ov.Core().available_devices)"
docker compose down
```

## 来源

- [固定上游比赛指南](../../external/physical-ai-studio/JUNCTION2026.md)
- [固定上游 Dockerfile](../../external/physical-ai-studio/application/docker/Dockerfile)
- [固定上游 Compose](../../external/physical-ai-studio/application/docker/docker-compose.yaml)
- [uv 的 PyTorch 后端选择](https://docs.astral.sh/uv/guides/integration/pytorch/)
