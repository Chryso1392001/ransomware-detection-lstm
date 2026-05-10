# 🔒 Deep Learning-Based Ransomware Detection in Encrypted Network Traffic

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow 2.13](https://img.shields.io/badge/TensorFlow-2.13-orange.svg)](https://www.tensorflow.org/)

> **Master's Thesis Project** - Carnegie Mellon University Africa  
> Detecting ransomware using LSTM neural networks on encrypted traffic metadata

---

## 🎯 Overview

Deep learning-based ransomware detection system operating entirely on **encrypted network traffic** without payload inspection. Using dual LSTM models with ensemble voting, achieving **95.15% accuracy** on historical ransomware and providing the **first empirical measurement of temporal model degradation** (15.86% over 4 years).

## 📊 Key Results

| Metric | Model V1 (2017) | Model V2 (2021) | Ensemble |
|--------|----------------|----------------|----------|
| **Accuracy** | **95.15%** | 79.29% | 67.25% |
| **Precision** | 98.53% | 91.45% | 63.78% |
| **Recall** | 94.08% | 64.35% | **96.67%** |
| **F1-Score** | 96.25% | 75.54% | 76.86% |

### Key Findings

1. **Temporal Degradation:** 15.86% accuracy decline over 4 years (3.97%/year) - **first empirical measurement**
2. **Cross-Generational Failure:** V1 achieves only 43% accuracy on modern threats
3. **Ensemble Recall:** 96.67% - catches nearly all ransomware attacks
4. **SIEM Integration:** 100% test success (19/19 passed), <5s latency

---

## 🏗️ System Architecture

Network Traffic → Zeek Sensor → Feature Extraction (23 features)
↓
┌───────────────┴───────────────┐
↓                               ↓
Model V1 (2017)               Model V2 (2021)
95.15% accuracy               79.29% accuracy
↓                               ↓
└───────────────┬───────────────┘
↓
Ensemble Voting (5 rules)
96.67% recall
↓
Wazuh SIEM Integration
MITRE ATT&CK T1486

---

## 📁 Repository Structure
ransomware-detection-lstm/
├── src/
│   ├── models/              # LSTM model training
│   │   ├── train_model_v1.py
│   │   ├── train_model_v2.py
│   │   └── ensemble_voting.py
│   ├── preprocessing/       # Feature extraction
│   ├── detection/           # Real-time detection
│   └── demo/                # Presentation demos
├── results/
│   ├── figures/             # Visualizations
│   └── performance/         # Metrics JSON
├── config/                  # Configuration files
├── wazuh/                   # SIEM integration
└── docs/                    # Documentation

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- TensorFlow 2.13+
- Zeek Network Monitor
- 8GB RAM minimum

### Installation

```bash
# Clone repository
git clone https://github.com/Chryso1392001/ransomware-detection-lstm.git
cd ransomware-detection-lstm

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Train models (requires datasets)
python src/models/train_model_v1.py
python src/models/train_model_v2.py

# Run detection
python src/detection/ransomware_detector.py

# Run demo
python src/demo/demo_full_pipeline.py
```

---

## 📈 Ransomware Families

### Model V1 (Historical - 2017)
- Cerber
- Locky  
- WannaCry

### Model V2 (Modern - 2019-2021)
- Ryuk
- REvil (Sodinokibi)
- Maze
- Phobos
- BitPaymer
- RansomX
- Razy

---

## 🔬 Research Contributions

1. **First Temporal Degradation Measurement** - Quantified 15.86% accuracy decline over 4 years
2. **Cross-Generational Failure Discovery** - 43% accuracy catastrophic failure on modern threats
3. **Security-First Ensemble System** - 96.67% recall through intelligent voting
4. **Production-Ready Integration** - Complete Wazuh SIEM integration
5. **Continuous Learning Framework** - Autonomous 1-3 month adaptation
6. **Encrypted Traffic Detection** - 95.15% accuracy without payload inspection

---

## 📚 Documentation

- [Project Summary](docs/PROJECT_FINAL_SUMMARY.md)
- [System Completion](docs/PHASE5_COMPLETION.md)
- [Production System](docs/FINAL_PRODUCTION_SYSTEM.md)
- [User Guide](docs/user_intervention_guide.md)

---

## 📄 Citation

```bibtex
@mastersthesis{ransomware2026,
  title={Deep Learning-Based Ransomware Detection in Encrypted Network Traffic Using LSTM Networks},
  author={[Your Name]},
  year={2026},
  school={Carnegie Mellon University Africa},
  type={Master's Thesis}
}
```

---

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 👨‍🎓 Author

**[Your Name]**  
Master's Student, Information Technology  
Carnegie Mellon University Africa

- 📧 Email: [your.email@andrew.cmu.edu]
- 💼 LinkedIn: [Your LinkedIn]

---

## 🙏 Acknowledgments

- **Supervisor:** [Supervisor Name]
- **Carnegie Mellon University Africa**
- **Stratosphere IPS Project** - Public ransomware datasets
- **Wazuh Community** - Open-source SIEM platform

---

**⭐ Star this repository if it helps your research!**
