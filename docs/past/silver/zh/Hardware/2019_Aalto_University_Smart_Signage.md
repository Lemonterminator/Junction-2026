# [2019] Aalto University — 智能标牌——学生为学生设计

## 元数据

- **年份**: 2019
- **挑战合作方**: Aalto University
- **原始历史赛道**: IoT & Hardware
- **2026 对应赛道**: Hardware Track (by Arduino)
- **技术细分方向**: 智能建筑、工业物联网与数字孪生 (Smart Buildings, Industrial IoT & Digital Twins)
- **核心主题**: 公寓楼宇智能信息屏（Smart Signage）硬件形态设计与暖通/水电/网络物联网数据集成
- **归类理由**: 原属 IoT & Hardware 赛道。针对 AYY 学生公寓 2600 套住房的楼道智能交互屏进行硬件与软件设计，接入楼宇暖通空调（HVAC）、水电能耗与网络负载等真实传感器数据。

---

## 挑战完整题目

智能标牌——学生为学生设计

## 挑战描述 (Description)

阿尔托大学学生会（AYY）拥有约2600套公寓，居住着约3500名租户。AYY一直计划在其公寓楼的楼梯间和走廊安装信息屏幕（智能标牌）。本次挑战旨在寻找这些“智能标牌”屏幕在硬件方面，但最重要的是在软件方面可以如何实现的解决方案和创意。它们可以显示哪些信息，可以包含哪些功能？

AYY希望看到关于哪些相关数据和功能可以整合到这些屏幕中的不同创意和概念。例如，这些数据可以包括建筑物的供暖、用水和用电消耗数据、网络使用数据、AYY的新闻和广告、自动更新的租户列表，以及各种有趣的功能，这些功能还可以在不同走廊和建筑物的屏幕之间运行。在最佳情况下，本次挑战的解决方案还可以改善居住在AYY住房中的学生之间的社区体验。

## 可用资源 (Resources)

AYY将提供：AYY的IT团队将在周末期间在线帮助您完成挑战。我们将带来一个来自我们其中一栋建筑的匿名网络使用数据和HVAC数据包供您使用。

---

## 历届获奖方案与验证项目

- **赛题第一名 (Winner)**：**AyyHello!**（Jesse Tolvanen、Satria Sutisna、Harri Rahikainen、Mari Porko、`smirq`）`[L1]` — 将被动式楼道广告牌改造为“树莓派 + 零接触体感”交互中枢：利用硬件 PIR 热释电传感器（`GPIO.BOARD Pin 11` 上升沿硬件中断与 `Pin 3` 状态灯）实现人员唤醒，USB 摄像头接入魔改 `MobilePose-PyTorch`（`ResNet-18 @ 224x224`），经 10 帧多数表决消抖后将手势指令（`L`/`R`/`U`）通过本地 `POST /dir` 推送至 Flask 服务（`:5000`），驱动 React `16.12.0` 看板实时展示 AYY 公寓真实电/热/水能耗月周数据、公交天气及体感小游戏。
- **硬件与工程经验**：将树莓派 GPIO 中断脚本（`pir.py`）、PyTorch 摄像头姿态识别（`run_webcam.py`）、建筑表计 CSV 清洗服务（`analysis.py`）与 React 展示界面经由本地 HTTP 解耦，使软硬件成员能并行联调；且 10 帧窗口投票消抖以极低算力解决了关键点闪烁问题。
- **Bronze 原始档案**：[`2019_Aalto_AYY_SmartSignage_AyyHello.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2019_Aalto_AYY_SmartSignage_AyyHello.md)
- **原始信源**：[Junction 2019 官方获奖公告 (Medium)](https://medium.com/hack-junction/the-winners-of-junction-2019-de539036dc3f) | [AyyHello! 开源仓库 (`mariporko/junction2019`)](https://github.com/mariporko/junction2019) | [阿尔托大学官网报道](https://www.aalto.fi/en/news/student-union-looks-for-creative-ideas-for-their-information-channels-from-junction)
