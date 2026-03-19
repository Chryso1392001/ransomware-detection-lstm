# 🛡️ Real-Time Ransomware Detection Using LSTM

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://www.tensorflow.org/)
[![Accuracy](https://img.shields.io/badge/Accuracy-95.15%25-success.svg)](results/)

> AI-powered ransomware detection using LSTM with transfer learning. Achieves 95.15% accuracy on encrypted traffic without decryption.

---

## 📊 **Performance Metrics**

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| **Accuracy** | ≥ 90% | **95.15%** | ✅ +5.15% |
| **Precision** | ≥ 85% | **98.53%** | ✅ +13.53% |
| **Recall** | ≥ 85% | **94.08%** | ✅ +9.08% |
| **F1-Score** | ≥ 0.85 | **0.9625** | ✅ +0.1125 |
| **FPR** | < 5% | **2.76%** | ✅ -2.24% |

**All 5 target metrics exceeded!** 🎉

---

## 🚀 **Quick Start**

### Installation
```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/ransomware-detection-lstm.git
cd ransomware-detection-lstm

# Install dependencies
pip install -r requirements.txt
```

### Usage
```bash
# Train model
python scripts/train_model_original.py

# Preprocess data
python scripts/preprocess_data.py

# Extract features
python scripts/extract_features_zeek_fixed.py
```

---

## 📁 **Repository Structure**
```
ransomware-detection-lstm/
├── scripts/           # Python training scripts
├── models/            # Trained LSTM model (507 KB)
├── results/           # Performance visualizations
├── data/              # Dataset information
└── docs/              # Documentation
```

---

## 🏗️ **Model Architecture**

- **Type:** LSTM with Transfer Learning
- **Parameters:** 129,857 (1.5 MB)
- **Training Time:** 15 epochs, ~10-15 minutes
- **Dataset:** 3,627 network flows
- **Features:** 23 behavioral features

---

## 🎯 **Key Innovation**

**Transfer Learning with Small Dataset**

Traditional deep learning needs 50,000+ samples. Our approach achieves 95.15% accuracy with only 3,627 samples using transfer learning - making it viable for resource-constrained environments.

---

## 👥 **Team**

**Group 13 - Final Year Project 2025-2026**

- **NAYISABYE Jean Chrysostome** (222002156) - Team Leader, Model Development
- **IKUZWE Pascaline** (222003736) - Data Engineering & Preprocessing
- **ICYITEGETSE Thersie** (222005658) - System Integration & Testing

**Institution:** University of Rwanda - College of Science and Technology  
**School:** School of ICT

---

## 📄 **License**

MIT License - See [LICENSE](LICENSE) file for details.

---

## 📞 **Contact**

**Project Inquiry:** [your-email@example.com]  
**Institution:** University of Rwanda - CST

---

**⭐ If you find this project useful, please consider giving it a star!**
