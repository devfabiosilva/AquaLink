# 💧 AquaLink — Remote Automation and Monitoring of Artesian Wells

> 🌎 *Bringing water to remote communities through open technology.*

![Status](https://img.shields.io/badge/Project_Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Platform](https://img.shields.io/badge/Platform-PLC%20%2B%20IoT%20Gateway-lightgrey)
![Connectivity](https://img.shields.io/badge/Connectivity-Satellite%20(Starlink%2FViasat)-blueviolet)

---

## 🇺🇸 About the Project

**AquaLink** is an **open-source** automation and remote monitoring system for artesian wells, designed to bring **efficiency, reliability, and connectivity**

It combines:
- **Industrial PLC** for automation and well protection  
- **IoT Gateway** for data collection and transmission  
- **Satellite Internet (Viasat or Starlink)** for real-time monitoring in remote locations  

---

### ⚙️ Features
- Real-time monitoring of water level, pressure, and flow  
- Automatic pump
- Fault and low-water alerts  
- Data logging via MQTT
- Modular, expandable architecture  

---

### 🔐 Security and Encryption
AquaLink implements **industrial-grade end-to-end security**, ensuring message integrity and authenticated control:

- 🔒 **Mutual SSL/TLS encryption:** both client and broker are signed and validated with SSL certificates.  
- 🧾 **HMAC-SHA256/512 digital signatures:** each message is signed and verified with a secure shared key.
- 🔑 **Two-Factor Authentication (2FA):** required for all PLC control commands.
- 🛰 **Secure MQTT communication:**

These layers ensure reliable and tamper-proof operation even over unstable satellite links.

---

### 🧩 Architecture
- **Hardware:** PLC + level, pressuresensors
- **IoT Gateway:** Modbus, MQTT communication  
- **Cloud:** dashboards and alerts
- **Connectivity:** satellite (Starlink/Viasat)

```text
         ┌────────────────────┐
         │   Level, Pressure  │
         │    and Flow Sensors│
         └──────────┬─────────┘
                    │
                    ▼
            ┌────────────────┐
            │      PLC       │
            │ (Local Control │
            │  and Safety)   │
            └───────┬────────┘
                    │ Modbus TCP
                    ▼
          ┌─────────────────────┐
          │     IoT Gateway     │
          │     (MQTT + SSL)    │
          └───────┬─────────────┘
                  │
                  ▼
        🌐 Satellite Link (Viasat / Starlink)
                  │
                  ▼
         ┌─────────────────────────────┐
         │         Cloud Server        │
         │ Dashboards • API • Storage  │
         └─────────────────────────────┘

``
---

### 🛰 Technologies
- PLC programmed in Ladder
- C, Python 3 and Java for driver and security implementation
- Linux-based gateway (Yocto/Debian)
- mbedTLS
- MQTT broker
- Database and web dashboard (Grafana, Node-RED, or custom)  
- SSL certificates and HMAC-based authentication  

---

### 👐 Contributing
Contributions are welcome!  
Open an **issue** or submit a **pull request** with improvements, documentation, or new modules.

---

### 📜 License
This project is licensed under the [MIT License](LICENSE).

