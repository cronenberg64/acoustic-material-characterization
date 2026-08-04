# Acoustic Material Characterization

This repository contains the software and firmware pipeline for characterizing material properties (such as density and Young's modulus) by analyzing acoustic impact sounds. 

The system relies on a physical testing rig (an ESP32-controlled solenoid) to strike material samples. The resulting acoustic waveform is captured, processed using physics-based modal feature extraction (identifying resonant frequencies and damping coefficients), and passed through a machine learning classifier to predict the material's properties.

## Getting Started

This project uses `uv` for lightning-fast Python package management. 

### 1. Install Dependencies
```bash
uv sync
```

### 2. Run the Machine Learning Harness
You can test the machine learning pipeline (Random Forest, K-Nearest Neighbors, Ridge Regression, etc.) without needing the physical rig.

**To run on perfectly synthesized acoustic data:**
```bash
uv run python -m ame.models.run_all --dataset synthetic
```

**To run a sanity check on real-world impact data (RealImpact Dataset):**
First, download and extract the RealImpact zip files into `RealImpact/dataset/`. Then run:
```bash
uv run python src/ame/data/import_real_impact.py --dir RealImpact/dataset
uv run python -m ame.models.run_all --dataset internet
```

## Data Acquisition (DAQ)

Once the physical rig is built (ESP32 + Solenoid + Microphone), you can use the DAQ scripts to collect real acoustic samples.

### Calibrate the Solenoid
Determines the correct pulse widths to achieve 5N, 10N, and 15N impact forces.
```bash
uv run python src/ame/daq/calibrate.py --port /dev/cu.usbserial-XXXX
```

### Run an Acquisition Session
Automatically iterates through sample IDs, strike locations, and force levels to build a comprehensive dataset.
```bash
uv run python src/ame/daq/acquire.py --port /dev/cu.usbserial-XXXX
```
*(Note: If no ESP32 is connected, the scripts will gracefully fall back to a mock/synthetic generation mode.)*

## Pipeline Architecture

1. **`ame.daq`**: Handles serial communication with the ESP32 to trigger the solenoid and records the microphone input.
2. **`ame.synth`**: A physics engine that generates realistic damped-sinusoid acoustic waveforms based on theoretical Hertzian impact models for software testing.
3. **`ame.features`**: Extracts both generic audio features (RMS, Zero-Crossing Rate, Spectral Centroid) and modal physics features (Peaks, Damping, Q-Factor).
4. **`ame.models`**: The Scikit-Learn evaluation harness that cross-validates regressors and classifiers on the extracted features.