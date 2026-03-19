# AeroGuard: Aviation Arrester System (AAS) Safety Monitor 🚧
> **Previously documented as: Arrester Barrier System**

![Build Status](https://img.shields.io/badge/AI--Research-Active-blue)
![Tech](https://img.shields.io/badge/Python-Flask-green)

### 📄 Overview
AeroGuard is a high-fidelity simulation and monitoring platform designed for **Aircraft Arrester Systems (BAK-15)**. The project addresses the critical safety challenge of monitoring net height and sagging during emergency flight arrestment operations.

### 🧠 Core Engineering & Math
This system moves beyond simple detection by implementing a **Digital Twin** environment:
- **Parabolic Modeling:** Uses mathematical catenary/parabolic equations to simulate real-time net sagging patterns.
- **Spatial Calibration:** Establishes a **Pixels-per-Meter (PPM)** ratio using airfield masts (5m) as a geometric baseline for monocular depth estimation.
- **Robustness (XAI):** Integrated **CLAHE (Contrast Limited Adaptive Histogram Equalization)** to maintain height accuracy during adverse weather (fog/haze) conditions.

### 🛠️ Key Features
- **Real-Time Telemetry:** Live vertical stability logs integrated with Chart.js.
- **Aviation HUD:** A professional-grade command center interface with safety threshold alarms (Critical at < 4.3m).
- **Synthetic Data Generation:** Engineered a synthetic video pipeline to validate algorithms in high-stakes airfield scenarios.

### 🚀 Tech Stack
- **Backend:** Flask, OpenCV, NumPy
- **Frontend:** Tailwind CSS, Chart.js, JavaScript (Async Fetch API)

---
Developed by **Bhuvitha Andurthi** | Computer Science & Engineering.
