# Dataset Documentation

## Overview
This directory contains dataset information for the ransomware detection project.

## Dataset Composition
- **Total:** 3,627 network flows
- **Normal:** 1,250 flows (34.5%)
- **Ransomware:** 2,377 flows (65.5%)

## Features (23 total)
- Temporal (3): duration, timestamp, packets_per_second
- Volume (10): bytes, packets, ratios, averages
- Behavioral (7): protocol, service, connection state, port
- TLS/SSL (3): version, cipher, server name

## Data Sources
- Private lab data (RanSim + normal traffic)
- Public PCAPs (Cerber, Locky ransomware)

**Note:** Raw dataset files are not included in repository due to size.
