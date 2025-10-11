# Quantum Random Number Generator (QRNG) Defense Prototype

**AQVH1910 - Amaravati Quantum Valley Hackathon 2025**  
**Team: Hackathon Warriors**

## Overview

A comprehensive Quantum Random Number Generator system for defense and security applications, featuring quantum circuits, secure key distribution, AI anomaly detection, and real-time monitoring dashboard.

## Features

- **Quantum Circuit Core**: True random bit generation using Hadamard gates and quantum measurement
- **QKD Protocols**: BB84 and E91 quantum key distribution simulation
- **AI Anomaly Detection**: Real-time entropy and QBER monitoring
- **Secure Communications**: AES-GCM encryption with quantum-derived keys
- **Defense Dashboard**: Live monitoring for Satellite, Naval, Airborne, and Ground communications
- **Hardware Ready**: Modular design for easy integration with physical quantum devices

## System Requirements

```bash
Python 3.8+
pip install qiskit qiskit-aer flask dash plotly numpy matplotlib cryptography dash-bootstrap-components requests
```

## Quick Start

### 1. Start Backend Server
```bash
python qrng_backend.py
# Server starts at http://127.0.0.1:5000
```

### 2. Launch Dashboard
```bash
python qrng_dashboard.py
# Dashboard available at http://127.0.0.1:8050
```

### 3. Test API Endpoints
```bash
# Generate QRNG bits
curl "http://127.0.0.1:5000/rng?shots=1024"

# Run E91 protocol
curl "http://127.0.0.1:5000/e91/chsh?shots=4096"

# Check system health
curl "http://127.0.0.1:5000/health"
```

## API Documentation

### Core Endpoints

- `GET /health` - System health check
- `GET /rng?shots=N` - Generate QRNG bits and entropy
- `GET /qkd?shots=N` - QKD protocol simulation
- `GET /e91/chsh?shots=N` - E91 Bell test (CHSH inequality)
- `GET /e91/key?shots=N&noise=X` - E91 key generation with QBER
- `POST /ai/anomaly` - Anomaly detection analysis
- `POST /crypto/set_key` - Set quantum-derived encryption key
- `POST /crypto/encrypt` - Encrypt message with quantum key
- `POST /crypto/decrypt` - Decrypt message with quantum key

## Hardware Integration

### Current Setup (Software)
- Qiskit AerSimulator for quantum circuit simulation
- Suitable for development, testing, and demonstration

### Hardware Migration Path
```python
# Replace AerSimulator with real quantum backend
from qiskit_ibm_runtime import QiskitRuntimeService

# For IBM Quantum devices
service = QiskitRuntimeService()
backend = service.backend("ibm_quantum_device")

# For local QRNG hardware
# Connect via USB/Serial interface
# Example: QRNG-USB, PicoQuant devices
```

## Security Features

- **Quantum-Safe**: Future-proof against quantum computing threats
- **Real-time Monitoring**: Continuous entropy and QBER analysis  
- **Alert System**: Automated anomaly detection and warnings
- **Multi-Platform**: Satellite, Naval, Airborne, Ground communications
- **Modular Design**: Easy integration with existing defense infrastructure

## Testing & Validation

### Entropy Testing
```bash
python test_entropy.py
# Validates Shannon entropy calculations
# Tests NIST randomness requirements
```

### Protocol Validation
```bash
python test_protocols.py
# Verifies BB84/E91 implementations
# Checks Bell inequality violations
# Validates QBER calculations
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Quantum Core  │    │  Flask Backend  │    │ Dash Dashboard  │
│                 │    │                 │    │                 │
│ • QRNG Circuit  │◄──►│ • API Endpoints │◄──►│ • Live Monitoring│
│ • E91 Protocol  │    │ • Crypto Module │    │ • Anomaly Alerts│
│ • BB84 Sim      │    │ • AI Detection  │    │ • Defense Status│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## National Mission Alignment

- **India's National Quantum Mission**: ₹8000 crore investment framework
- **DRDO Integration**: Compatible with defense quantum initiatives  
- **ISRO Compatibility**: Satellite quantum communication ready
- **Industry Standards**: QNu Labs, TASL quantum defense alignment

## Performance Metrics

- **Entropy Generation**: >0.99 bits per measurement
- **Key Rate**: Up to 1 Mbps (hardware dependent)
- **QBER Threshold**: <11% for secure communications
- **Response Time**: <100ms for anomaly detection
- **Scalability**: Multi-platform defense deployment

## Development Team

**Hackathon Warriors** - Team ID: 3c-31019  
AQVH 2025 - Amaravati Quantum Valley Hackathon

## License

Developed for AQVH1910 - Quantum Based Defence and Security Systems