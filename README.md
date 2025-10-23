# Mowbot Fleet Dashboard

AGV Fleet Management System with VDA5050 compatibility and dual language support.

## Features

- **🌍 Dual Language Support**: English and Korean with automatic language persistence
- **🤖 AGV Fleet Management**: Real-time monitoring and control
- **🗺️ Interactive Maps**: PyDeck-based mission planning and visualization
- **📡 MQTT Communication**: VDA5050 protocol support
- **🔒 Secure Configuration**: Encrypted broker settings storage
- **⚡ Real-time Updates**: Live AGV status and mission tracking

## Language Support

The dashboard supports multiple languages with automatic preference saving:

- **English (en)** - Default language
- **한국어 (ko)** - Korean language support
- **Auto-save** - Language preference persists across sessions
- **Easy switching** - Change language in Settings page

## Quick Start

```bash
cd mowbotfleet-dashboard
pip install -r requirements.txt
streamlit run app.py
```

## Configuration

1. **Language**: Set in Settings → Language Settings
2. **MQTT Broker**: Configure in Settings → Broker Configuration  
3. **Map Settings**: Adjust heading offset and display options
