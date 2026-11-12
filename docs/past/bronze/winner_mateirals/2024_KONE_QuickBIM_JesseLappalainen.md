# [2024 Winner Case Study] KONE — QuickBIM (Junction 2024 全场总季军)

## 1. 元数据概览 (Metadata)
- **对应赛题文件**: `2024_KONE_BIM_for_any_building_by_anyone.md`
- **出题方 (Partner)**: KONE (通力电梯)
- **赛题名称**: BIM for any building, by anyone.
- **获奖项目**: **QuickBIM**
- **获奖团队**: Mankeli Software (Jesse Lappalainen, Miska, Lauri)
- **获奖荣誉**: **Junction 2024 全场总季军 (3rd Place Overall)** 及 KONE 挑战赛第一名
- **开源仓库**: [GitHub - Mankeli-Software/quickbim](https://github.com/Mankeli-Software/quickbim)
- **官方深度复盘**: [Jesse Lappalainen Blog - Junction 2024](https://www.jemlap.fi/blog/junction-2024)

---

## 2. 方案与技术架构
- **核心功能**: 上传任意平面图 SVG / 建筑图纸，利用 OpenCV 自动提取墙体、门窗轮廓，通过后台容器化 Blender 引擎毫秒级生成高精度 3D BIM 建筑模型，并在 Web 与移动端 AR 中交互式精准摆放通力电梯。
