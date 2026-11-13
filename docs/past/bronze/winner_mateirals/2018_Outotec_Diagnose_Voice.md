# Outotec — "I Hear Voices in My Factory" Verification & Acoustic Diagnosis Entry (Junction 2018)

- **Event / Year**: Junction 2018 (Aalto University, Espoo, November 23–25, 2018)
- **Track & Challenge**: **Intelligent Manufacturing / Industrial IoT** — *"I hear voices in my factory"* (**Outotec**)
- **Silver Challenge Spec**: [2018_Outotec_I_Hear_Voices_In_My_Factory.md](file:///c:/Users/Jiang/.gemini/antigravity/scratch/hackjunction/docs/past/silver/en/Hardware/2018_Outotec_I_Hear_Voices_In_My_Factory.md)
- **Verification Tier**: **No Verified Official Winner Record Found** *(L1 Public Participant Submission Repository Verified: `ismajilv/diagnose-outotec-voice`)*
- **Official Winner Status**: After searching Devpost (`junction-2018.devpost.com` & `site:devpost.com/software`), Medium (`hack-junction`), Outotec / Metso public newsrooms, and GitHub, **no verified public record names the official 1st-place winner** of Outotec's 2018 challenge.
- **Primary URLs (Verified Submission)**:
  - GitHub Repository: https://github.com/ismajilv/diagnose-outotec-voice
  - Linked Pitch Deck (referenced in repo): Google Slides `1Xs_0dQA_T5WtxK8GnS10yOMN2JfAHo9xW8nufiCNyDk`

---

## Verified Challenge Submission (`diagnose-outotec-voice`)

### Team & Authors
- **Tural Ismayilov** (`ismajilv`), **Said Kazimov**, **Gunay Abdullayeva**, **Turxan Badalov** *(submitted as a verified Junction 2018 Outotec challenge entry; placement unknown / unconfirmed)*

### Technical Architecture Observed (`Audio Prediction.ipynb` & Repo Files)
1. **Challenge Dataset Modality**: Outotec provided multimodal industrial machine-health telemetry containing **WAV acoustic recordings** (labeled operational states including `Stopped`, `Good`, etc.), **CSV** time-series measurements, and **motion JSON** files.
2. **DSP Feature Extraction**: Uses Python **`librosa`** (`res_type='kaiser_fast'`) to resample industrial audio clips and extract **40-dimensional mean MFCC** (Mel-Frequency Cepstral Coefficient) acoustic feature vectors per sample.
3. **Edge-Ready Neural Classifier**: Trains a **Keras `Sequential` Multi-Layer Perceptron (MLP)** (`Dense(256, activation='relu')`, `Dropout(0.3)`, ...; optimizer **`Adam`**, **`batch_size=16`**, **`epochs=60`**) to classify industrial acoustic health states (`Good` vs. fault/stopped states).

---

## Transferable Insights for Industrial Acoustic Predictive Maintenance

1. **Challenge Telemetry Blueprint**: Outotec's Junction 2018 dataset explicitly combined factory **audio (WAV)** with **motion/vibration JSON** and **structured CSV** logs — reflecting real mineral-processing predictive maintenance pipelines where acoustic anomalies precede bearing or crusher failures.
2. **Baseline Embedded ML Footprint**: A **40-MFCC + small Dense MLP** pipeline is compact enough to deploy on industrial edge gateways without GPU inference servers.

---

## Sources & Verification Notes

- **L1 Verified Participant Code**: https://github.com/ismajilv/diagnose-outotec-voice (`Audio Prediction.ipynb`, commit history, Google Slides deck ID `1Xs_0dQA_T5WtxK8GnS10yOMN2JfAHo9xW8nufiCNyDk`).
- **Search Verification**: Checked GitHub search (`"Outotec" "Junction 2018"`), Devpost, Metso/Outotec reports/press releases, and Medium; no official Outotec 1st-place winner roster is publicly indexed.
