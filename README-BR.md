# 💧 AquaLink — Automação e Monitoramento Remoto de Poços Artesianos

> 🌎 *Bringing water to remote communities through open technology.*  
> 💡 *Levando água a comunidades isoladas com tecnologia aberta.*

![Status](https://img.shields.io/badge/Project_Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Platform](https://img.shields.io/badge/Platform-PLC%20%2B%20IoT%20Gateway-lightgrey)
![Connectivity](https://img.shields.io/badge/Connectivity-Satellite%20(Starlink%2FViasat)-blueviolet)

---

## 🇧🇷 Sobre o Projeto

**AquaLink** é um projeto **open source** de automação e monitoramento remoto de poços artesianos, criado para levar **eficiência, confiabilidade e conectividade**.

O sistema combina:
- **CLP industrial** para automação e proteção do poço
- **Gateway IoT** para coleta e envio de dado
- **Conexão via satélite (Viasat ou Starlink)** para monitoramento em tempo real, mesmo em locais isolados  

---

### ⚙️ Funcionalidades
- Monitoramento de nível de água, pressão e vazão
- Controle automático da bomba
- Alertas de falhas e níveis críticos  
- Registro de dados via MQTT  
- Arquitetura modular e expansível  

---

### 🔐 Segurança e Criptografia
AquaLink implementa um **padrão de segurança de nível industrial**, garantindo integridade e autenticação de ponta a ponta:

- 🔒 **Criptografia SSL/TLS mútua:** certificado assinado tanto no **cliente quanto no broker**, com autenticação de via dupla.  
- 🧾 **Assinatura digital HMAC-SHA256/512:** cada mensagem é validada com chave secreta e assinatura criptográfica.  
- 🔑 **Autenticação de dois fatores (2FA):** exigida para comandos críticos de controle do CLP.
- 🛰 **Protocolo MQTT seguro:**

Essas camadas de segurança garantem operação confiável mesmo em redes instáveis, como conexões via satélite.

---

### 🧩 Arquitetura
- **Hardware:** CLP + sensores de pressão
- **Gateway IoT:** comunicação via Modbus TCP, MQTT  
- **Nuvem:** dashboards e notificações
- **Conexão:** satélite (Starlink/Viasat)

---

### 🛰 Tecnologias Utilizadas
- CLP com lógica
- C, Python 3 e Java para assinatura e 2FA
- MBEDTLS
- Gateway Linux embarcado (Yocto/Debian)  
- Broker MQTT
- Banco de dados e dashboard web (Grafana, Node-RED ou custom)  
- Certificados SSL e chaves HMAC para autenticação segura  

---

### 👐 Contribuição
Contribuições são bem-vindas!  
Abra uma **issue** ou envie um **pull request** com melhorias, documentação ou novos módulos.

---

### 📜 Licença
Este projeto está licenciado sob a [MIT License](LICENSE).

---


