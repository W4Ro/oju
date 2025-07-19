# Oju

**Open-source cybersecurity monitoring platform.**

Oju provides automated surveillance and threat detection for organizational entities and their websites through comprehensive scanning, real-time alerting, and incident response coordination.

## Features

- **Multi-Platform Monitoring**: SSL certificates, domain security, website defacement, availability
- **Entity Management**: Organize monitoring by organizations and their platforms  
- **Real-Time Dashboard**: Centralized security metrics and alert visualization
- **Automated Alerting**: Notification system with focal point management
- **Incident Response**: RTIR integration for automated ticket creation
- **Threat Intelligence**: VirusTotal integration for threat detection

## Quick Install

### Prerequisites
- Docker Engine 20.10+ and Docker Compose 1.29+
- 2GB RAM (4GB recommended)
- 40GB disk space
- Ports 80 and 443 available

### Installation
```bash

# Clone and install manually
git https://github.com/bjCSIRT/oju.git
cd oju

# on linux based system
./install.sh

# or on windows
.\install.ps1
```

### Access
- **Web Interface**: https://your-domain.com
- **Default Login**: Configure during installation

## Architecture

**Stack**: Django + Vue.js + PostgreSQL + Redis + Celery + Nginx

**Services**:
- Django backend with REST API
- Vue.js frontend interface  
- PostgreSQL database
- Redis caching and task queue
- Celery workers for monitoring
- Nginx reverse proxy with SSL

## Monitoring Types

| Category | Description |
|----------|-------------|
| **SSL Problems** | Invalid/expired certificates |
| **Domain Issues** | DNS/domain accessibility problems |
| **Defacement** | Unauthorized content modifications |
| **Availability** | Website inaccessibility |
| **VirusTotal** | Threat detection and analysis |

## Integrations

- **RTIR**: Automated incident response ticketing
- **VirusTotal**: Threat detection and malware scanning
- **Cerebrate**: Organizational data synchronization

## Documentation

Complete documentation available at: https://bjcsirt.github.io/oju-docs/

- Installation Guide
- User Manual  
- API Reference
- Integration Setup

## Support

- **Issues**: GitHub Issues
- **Contact**: bjcsirt@asin.bj
- **Documentation**: [Oju DOCS](https://bjcsirt.github.io/oju-docs/)

## License

Open-source project - see LICENSE file for details.