# [2018] Ensto — 教电动汽车充电器新技巧

## 元数据

- **年份**: 2018
- **挑战合作方**: Ensto
- **原始历史赛道**: IoT & Hardware
- **2026 对应赛道**: Hardware Track (by Arduino)
- **技术细分方向**: 智能能源、电动出行与车载硬件 (Smart Energy, EV Charging & Mobility Hardware)
- **核心主题**: 基于硬件开发板与 Ensto 物联网平台的智能电动汽车充电桩功能扩展
- **归类理由**: 原属 IoT & Hardware 赛道。要求在现场提供的硬件开发板（Development Boards）上开发新功能，并与 Ensto 智能充电桩 IoT 后端 REST API 深度集成。

---

## 挑战完整题目

教电动汽车充电器新技巧

## 挑战描述 (Description)

汽车充电远不止插上电源给电池充电那么简单。汽车会在家庭、工作场所、酒店、购物中心、停车场和机场等场所充电，仅举几例，而在所有这些场所中，用户可能有不同的需求。在一个或多个细分场景中，为电动汽车驾驶员创造最佳的充电体验。利用 Ensto 平台提供的 REST API 以及在提供的开发板上开发的附加功能来实现/演示此解决方案。您还可以利用我们从后端服务中已收集的 IoT 数据来完善您的解决方案。

---

## 历届获奖方案与验证项目

- **Ensto 赛道第一名兼 Junction 2018 全场总冠军 🏆 (€20,000)**：**Oneiro (Team Glados)**（Teemu Taskula、Andreas Urbanski、Ville Toiviainen — 继 2017 *Signvision* 后连续两年蝉联 Junction 全场总冠军）`[L1]`/`[L2]` — 打造无刷卡、无手动鉴权的“共享充电桩 Airbnb”：车位侧部署 **Raspberry Pi + PiCamera**（`systemd photographer.service`），每 `0.5 秒`（`2 s` 超时）抓拍 `640x480` JPEG 推流至 AWS Sanic 后端与 Docker 化的 **`openalpr:16.04`**（欧盟/芬兰车牌识别阈值 `confidence >= 75`），置信达标后自动通过 EnstoFlow REST/OCPP v1 API 解锁实体 **Ensto Chago** 充电桩（`JunctionEVB1`）开始供电与计费，配套 React Native Expo 客户端与基于 Telia 蜂窝人流数据的 Mapbox GL 选址热力图。
- **硬件与工程经验**：在代码架构中利用 `LIVE_MODE=true` 将实体桩（`JunctionEVB1`）与模拟测试桩（`oneiro` / `junction-6`）干净隔离，严格监控充电桩状态机 LED 指示灯转换与 OCPP 心跳，并将端侧车牌识别无缝衔接至清晰的车位分享商业收益分成模型（`0.25 €/h` + `0.6 €/h`, `owners_cut = 0.70`），一举赢得全场互评最高票与 Ensto 软件总监赞誉。
- **Bronze 原始档案**：[`2018_Ensto_Oneiro_Glados.md`](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/bronze/winner_mateirals/2018_Ensto_Oneiro_Glados.md)
- **原始信源**：[GitHub (`teamglados/oneiro`)](https://github.com/teamglados/oneiro) | [Vimeo 演示](https://vimeo.com/302650304) | [Mobiili.fi 报道](https://mobiili.fi/2018/11/25/junction-hackathon-espoossa-paattyi-latauspisteiden-airbnbn-voittoon-sama-tiimi-voitti-kilpailun-viime-vuonnakin/) | [Talotekniikka-lehti](https://talotekniikka-lehti.fi/oneiro-voitti-junction-2018-hackathonin/)
