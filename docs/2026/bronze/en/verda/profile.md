# Verda (Formerly DataCrunch / Verda Cloud) — Junction 2026 Partner In-Depth Research Report

## 1. Company Overview

- **Full Company Name**: Verda Cloud Oy (Formerly DataCrunch Oy)
- **Global Headquarters**: Helsinki, Finland, operating green high-performance computing (HPC) and AI data center clusters across Finland and Iceland.
- **Founding Background**:
  - Founded in 2020 in Helsinki, Finland, by **Ruben Bryon** (Founder & CEO).
  - The company grew out of local Helsinki machine learning meetups. At the time, researchers and startup founders grappling with large language models and deep neural networks were hindered by exorbitant public cloud GPU pricing, tedious quota waitlists, and convoluted configuration overhead.
  - The founding team began by engineering custom bare-metal GPU server clusters powered by Nordic renewable energy, providing AI researchers with instant, frictionless, transparently priced, and 100% green compute.
  - **Brand Evolution**: In late 2025, as operations scaled from bare-metal GPU leasing into a full-stack AI hyperscaler encompassing instant multi-node clusters, serverless containers, and high-throughput parallel storage, DataCrunch rebranded as **Verda**. The name evokes "truth" (Verdad in Spanish) and "green" (Verda in Esperanto), signifying radical compute transparency and environmental sustainability.
- **Industry & Technical Standing**:
  - **Emerging European AI Unicorn**: Verda closed a landmark Series B funding round led by Silicon Valley venture firm Emergence Capital, with continued backing from Tesi (Finnish Industry Investment), Lifeline Ventures, byFounders, and J12 Ventures, driving enterprise valuation past the $1 billion milestone.
  - **Sovereign Green AI Hyperscaler**: Unlike legacy data centers dependent on fossil fuels or water-intensive evaporative cooling, Verda’s data centers in Finland and Iceland run on 100% hydroelectric and geothermal/wind energy with record-low Power Usage Effectiveness (PUE). Server waste heat is redirected directly into municipal district heating grids in Helsinki and neighboring regions.
  - **Tier-1 Hardware Fleet Availability**: Early European deployment of NVIDIA's latest architectures, providing large-scale production clusters of NVIDIA H100, H200, L40S, and next-generation Blackwell (B200 / GB300) systems interconnected via low-latency InfiniBand.

---

## 2. Core Products & Technical Architecture

Verda provides high-performance cloud infrastructure engineered specifically for the end-to-end AI/ML development lifecycle—from single-card rapid prototyping to multi-thousand-GPU distributed foundation model training and low-latency inference.

### 2.1 Flagship Compute Products
- **GPU Cloud Virtual Machines**:
  - Instant on-demand GPU instances preconfigured with Ubuntu LTS, NVIDIA Drivers, CUDA, cuDNN, and Docker/NVIDIA Container Toolkit.
  - Granular per-second/per-hour billing with no mandatory long-term lock-in or hidden ingress/egress fees.
- **Bare Metal GPU Servers**:
  - Dedicated hardware direct access eliminating hypervisor overhead, featuring full PCIe Gen5 and NVLink interconnect bandwidth for maximum compute efficiency.
- **Instant Multi-Node AI Superclusters**:
  - Interconnected by NVIDIA Quantum-2 800Gb/s InfiniBand fabrics, delivering ultra-low latency and non-blocking bi-directional bandwidth for massive pre-training and distributed fine-tuning frameworks (DeepSpeed, Megatron-LM, PyTorch FSDP).
- **Serverless AI Containers & Inference**:
  - Deploy Docker containers or model checkpoints directly; the managed control plane handles cold-start caching, automated scale-to-zero, and dynamic load balancing.
- **AI-Optimized NVMe Storage**:
  - High-throughput parallel shared filesystem delivering multi-million IOPS to prevent I/O starvation during massive multimodal dataset ingestion.

### 2.2 Developer Platform & Toolchain
- **Verda CLI (`verda-cli`)**:
  - High-performance, cross-platform CLI written in Go for automated cluster provisioning and lifecycle management:
    ```bash
    # Inspect GPU availability across zones
    verda availability --location FIN-01

    # Programmatically provision an on-demand GPU instance
    verda vm create --kind gpu --instance-type 1V100.6V \
        --location FIN-01 --os ubuntu-24.04-cuda-13.0-open-docker \
        --os-volume-size 100 --hostname junction-ai-node

    # Monitor real-time account burn rate and balance
    verda cost running
    verda cost balance
    ```
- **RESTful API & SDKs**:
  - Clean, open REST APIs enabling programmatic orchestration via CI/CD pipelines, Kubernetes (K8s Operators), Ray, and Slurm clusters.
- **Verda Cloud Console**:
  - Modern web management portal featuring real-time GPU telemetry, temperature/utilization monitoring, SSH key deployment, and unified billing dashboards.

---

## 3. Vision and Mission

### 3.1 Official Mission
> *"To make access to cutting-edge GPU compute as easy and frictionless as possible without compromising user experience, data protection, regulatory compliance, or sustainability."*

### 3.2 Official Vision
> *"To build Europe's premier sovereign, full-stack, 100% green-energy AI hyperscaler — delivering high-performance, cost-effective, and environmentally responsible computing power to empower global builders and researchers to solve humanity's greatest challenges."*

### 3.3 Core Philosophy
- **Sustainability First**: Leveraging Arctic natural free cooling and circular district heating heat re-injection, rejecting high-carbon compute growth.
- **Developer Frictionless**: Eliminating bureaucratic sales cycles, opaque quota gates, and surprise enterprise invoices; spinning up production clusters in minutes.
- **European Data Sovereignty**: Full compliance with EU GDPR and the EU AI Act, ensuring sovereign, auditable compute environments for enterprises and research labs.

---

## 4. Category & Classification

- **Primary Category**: AI Infrastructure & GPU Cloud
- **Secondary Categories**:
  - High-Performance Computing (HPC Clusters)
  - Green Computing & Sustainable Data Centers
  - Serverless AI Workload Orchestration
  - Cloud Platform-as-a-Service (PaaS)

---

## 5. Role at Junction 2026 & Challenge Tracks Prediction

### 5.1 Hackathon Partner Positioning
Verda serves as the core challenge sponsor and compute foundation provider for the **AI Infrastructure** track at Junction 2026.
During 48-hour sprints, teams often encounter hardware bottlenecks, out-of-memory (OOM) errors on laptops, or cumbersome enterprise cloud onboarding. Verda equips hackathon participants with substantial, frictionless cloud GPU credits and CLI access, enabling rapid fine-tuning of open-source models, multimodal diffusion training, and complex reinforcement learning experiments.

### 5.2 Challenge Tracks Prediction & Potential Prompts
1. **Green AI & Sustainable Inference Challenge**:
   - *Challenge Concept*: As generative AI energy consumption surges, how can teams leverage quantization (AWQ, GGUF, FP8/FP4), speculative decoding, or intelligent continuous batching to maximize inference tokens per kilowatt-hour?
   - *Solution Approach*: Deploy open-source models across Verda’s green Finnish clusters, benchmarking latency, GPU memory footprint, and power draw to create a carbon-aware inference routing gateway.
2. **Serverless AI Agents & Real-Time Orchestration**:
   - *Challenge Concept*: Engineer an autonomous agent platform that spins up fine-tuned task-specific adapters (LoRA) on demand in seconds, scaling compute down to zero when idle.
   - *Solution Approach*: Utilize the Verda CLI and REST API to construct a dynamic orchestration controller handling prompt routing and instance provisioning programmatically.
3. **Physical & Scientific AI Supercomputing**:
   - *Challenge Concept*: Accelerate open-source scientific foundation models (e.g., OpenFold, ClimaX weather forecasting) using multi-GPU parallel pipelines.
   - *Solution Approach*: Harness Verda’s InfiniBand multi-node infrastructure for distributed physical simulation and visualize results through an interactive web dashboard.

### 5.3 Quickstart Guide for Hackathon Teams
- **Step 1**: Register on the Verda Cloud Console and redeem the official Junction Hackathon compute coupon.
- **Step 2**: Install `verda-cli`, register your public SSH key, and provision an instance:
  ```bash
  # Spin up an NVIDIA H100 node with pre-installed CUDA drivers
  verda vm create --kind gpu --instance-type 1H100.80GB \
      --location FIN-01 --hostname junction-ai-core
  ```
- **Step 3**: Launch a container running vLLM, TGI, or Ollama to serve an OpenAI-compatible endpoint:
  ```bash
  docker run --gpus all -v /data:/models -p 8000:8000 \
      vllm/vllm-openai:latest --model mistralai/Mistral-7B-Instruct-v0.3
  ```

---

## 6. Official Links & Key Resources

- **Verda Official Website**: [https://verda.com](https://verda.com)
- **Verda Cloud Console**: [https://console.verda.com](https://console.verda.com)
- **Developer Documentation**: [https://docs.verda.com](https://docs.verda.com)
- **Verda Official CLI GitHub**: [https://github.com/verda-cloud/verda-cli](https://github.com/verda-cloud/verda-cli)
- **API Reference**: [https://docs.verda.com/api-reference](https://docs.verda.com/api-reference)
- **Instance Types & Pricing**: [https://verda.com/pricing](https://verda.com/pricing)
- **Sustainability & Green Computing Whitepaper**: [https://verda.com/sustainability](https://verda.com/sustainability)
