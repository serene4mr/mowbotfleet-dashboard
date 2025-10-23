# Streamlit Community Cloud Deployment Guide

## 🚀 Deployment Steps

### 1. **Prepare Repository**
Ensure your repository is public and contains:
- ✅ `mowbotfleet-dashboard/app.py` as main file
- ✅ `requirements.txt` with all dependencies
- ✅ `.streamlit/config.toml` for configuration
- ✅ All translation files in `translations/`

### 2. **Deploy to Streamlit Community Cloud**

1. Go to [Streamlit Community Cloud](https://share.streamlit.io/)
2. Click "New app"
3. Connect your GitHub repository
4. Configure deployment:
   - **Repository**: `your-username/mowbot_fleet`
   - **Branch**: `main`
   - **Main file path**: `mowbotfleet-dashboard/app.py`
   - **Python version**: `3.11`

### 3. **Configure Environment Variables**

Set these in Streamlit Cloud settings:

```bash
# MQTT Broker Configuration
BROKER_HOST=your-mqtt-broker.com
BROKER_PORT=8883
BROKER_USE_TLS=true
BROKER_USERNAME=your-username
BROKER_PASSWORD=your-password

# Optional: Mapbox API Key
MAPBOX_API_KEY=your-mapbox-api-key
```

### 4. **Configure Secrets (Alternative to Environment Variables)**

Create `.streamlit/secrets.toml` in your repository:

```toml
[broker]
host = "your-mqtt-broker.com"
port = 8883
use_tls = true
username = "your-username"
password = "your-password"

[mapbox]
api_key = "your-mapbox-api-key"
```

## ⚠️ **Streamlit Community Cloud Limitations**

### **🔄 Session Timeout Issues:**
- **Sessions timeout** after inactivity
- **MQTT connections drop** when session expires
- **Real-time updates stop** after a while

### **💡 Solutions Implemented:**

#### **1. Auto-Reconnection:**
- **Connection monitoring** every 30 seconds
- **Automatic reconnection** when connection drops
- **Session health checks** to detect timeouts

#### **2. Memory Optimization:**
- **Data retention limits** (last 100 entries)
- **Session cleanup** to prevent memory leaks
- **Efficient data handling** for cloud constraints

#### **3. User Experience:**
- **Connection status indicators** in sidebar
- **Manual refresh button** for reconnection
- **Session duration display** to track usage

## 🛠️ **Troubleshooting**

### **Common Issues:**

#### **1. Updates Stop After a While:**
- **Cause**: Session timeout or connection drop
- **Solution**: Use the "Refresh Connection" button in sidebar
- **Prevention**: The app now auto-detects and reconnects

#### **2. Connection Lost:**
- **Cause**: MQTT broker connection drops
- **Solution**: Check broker settings and network connectivity
- **Auto-fix**: App attempts automatic reconnection

#### **3. Memory Issues:**
- **Cause**: Too much data in session state
- **Solution**: App automatically cleans old data
- **Prevention**: Data retention limits implemented

### **🔧 Manual Recovery:**

If the app stops updating:

1. **Click "Refresh Connection"** in the sidebar
2. **Check broker settings** in Settings page
3. **Refresh the browser page** if needed
4. **Verify MQTT broker** is accessible from Streamlit Cloud

## 📊 **Performance Optimization**

### **For Streamlit Community Cloud:**

1. **Use external data sources** for large datasets
2. **Implement caching** for static data
3. **Optimize MQTT connection** handling
4. **Monitor resource usage** during testing
5. **Consider data pagination** for large datasets

### **Best Practices:**

- **Keep sessions lightweight**
- **Use efficient data structures**
- **Implement proper error handling**
- **Monitor connection status**
- **Provide user feedback** for connection issues

## 🚨 **Important Notes**

### **Limitations:**
- **Limited concurrent users** per app
- **Resource constraints** (CPU/Memory)
- **Session duration limits**
- **Public repository requirement**

### **Recommendations:**
- **Test thoroughly** before production use
- **Monitor performance** regularly
- **Consider upgrading** for high-traffic usage
- **Use external services** for critical data storage

## 🔄 **Auto-Recovery Features**

The app now includes:

- ✅ **Automatic connection monitoring**
- ✅ **Session health checks**
- ✅ **Memory optimization**
- ✅ **Connection status display**
- ✅ **Manual refresh options**
- ✅ **Error handling and recovery**

These features help mitigate the common issues with Streamlit Community Cloud deployment!
