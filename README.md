🕵️‍♂️ Operation SCEPTER: Stealthy Credential Expert Probing Tool for Enumeration and Reconnaissance

SCEPTER is your trusty sidekick in the world of cybersecurity, sniffing out MFA and SSO implementations like a digital bloodhound! 🐕‍🦺

🔍 What is SCEPTER?

SCEPTER (Stealthy Credential Expert Probing Tool for Enumeration and Reconnaissance) is a Python-based utility that scans websites for signs of Multi-Factor Authentication (MFA) and Single Sign-On (SSO) implementations. Like a medieval ruler's scepter, it grants you the power to reveal hidden security measures with a simple command. Bow before the mighty SCEPTER! 👑

✨ Features

🕵️‍♀️ Stealthy Reconnaissance: Quietly probes websites without triggering security alarms.

🧠 Expert Detection: Utilizes advanced pattern matching to identify popular MFA/SSO providers.

🔬 Comprehensive Enumeration: Analyzes both HTML content and JavaScript files for thorough detection.

🦾 Flexible Operation: Supports single URL or bulk processing from a file.
 
📊 Clear Intelligence: Provides output in both human-readable and machine-parsable formats.

🚀 Parallel Processing: Scans multiple URLs simultaneously for faster results.
  
🔌 Plugin System: Easily extend SCEPTER's capabilities with custom provider detections.

📜 Custom Rules: Define your own detection patterns via YAML configuration.

🛠 Installation

Clone this repository:

```
git clone https://github.com/queencitycyber/SCEPTER
cd SCEPTER
```

🚀 Usage
Wield the SCEPTER with these magical incantations:

```
python scepter.py -u https://example.com
python scepter.py -i urls.txt -o json
python scepter.py -u https://example.com -v --log-level DEBUG
```

🎭 Options

```
-u, --url: Specify a single URL to probe
-i, --input: Provide a file containing multiple URLs to investigate
-o, --output: Choose your preferred output format (text or json)
-v, --verbose: Unleash the full power of verbose output
--log-level: Control the chattiness of the logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

🎯 Supported MFA/SSO Providers
SCEPTER can detect a variety of authentication providers, including:

- Duo Security 🔐
- Microsoft Entra ID 🪟
- Okta 🔵
- RSA SecurID 🔑
- CrowdStrike Falcon 🦅
- Auth0 🔒
- OneLogin 1️⃣
- PingIdentity 🏓
- ForgeRock 🏔
- Generic SAML and OAuth implementations 🌐

