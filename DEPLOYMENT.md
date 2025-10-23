# 🚀 Streamlit Community Cloud Deployment Guide

This guide explains how to deploy the Mowbot Fleet Dashboard to Streamlit Community Cloud.

## 📋 Prerequisites

- GitHub repository with the code
- Streamlit Community Cloud account
- MQTT broker credentials (for production)

## 🔧 Deployment Steps

### 1. **Prepare Repository**
Ensure your repository has:
- ✅ `mowbotfleet-dashboard/app.py` as the main file
- ✅ `requirements.txt` with all dependencies
- ✅ GitHub Actions workflow (`.github/workflows/deploy-streamlit.yml`)

### 2. **Deploy to Streamlit Community Cloud**

1. **Go to [Streamlit Community Cloud](https://share.streamlit.io/)**
2. **Click "New app"**
3. **Connect your GitHub repository**
4. **Configure deployment:**
   - **Repository**: `your-username/mowbot_fleet`
   - **Branch**: `main`
   - **Main file path**: `mowbotfleet-dashboard/app.py`
   - **Python version**: `3.11`

### 3. **Environment Configuration**

#### **Required Environment Variables:**
```bash
# Optional: Override default broker settings
BROKER_HOST=your-mqtt-broker.com
BROKER_PORT=8883
BROKER_USE_TLS=true
BROKER_USERNAME=your-username
BROKER_PASSWORD=your-password
```

#### **Secrets Management:**
- Use Streamlit's secrets management for sensitive data
- Create `secrets.toml` in your repository root:

```toml
# secrets.toml
[broker]
host = "your-mqtt-broker.com"
port = 8883
use_tls = true
username = "your-username"
password = "your-password"

[mapbox]
api_key = "your-mapbox-api-key"
```

### 4. **Post-Deployment Configuration**

1. **Access the deployed app**
2. **Go to Settings page**
3. **Configure MQTT broker:**
   - Enter broker host and port
   - Enable TLS if using cloud broker
   - Enter credentials
   - Click "Save & Reconnect"

## 🔍 GitHub Actions Integration

The repository includes automated deployment validation:

### **Workflow Features:**
- ✅ **Dependency installation** - Ensures all packages are available
- ✅ **Test execution** - Runs pytest to validate functionality
- ✅ **App structure validation** - Checks Streamlit app configuration
- ✅ **Configuration validation** - Verifies broker config manager
- ✅ **Deployment readiness** - Confirms app is ready for deployment

### **Trigger Events:**
- **Push to `main`** - Automatic validation and deployment
- **Pull requests to `main`** - Pre-deployment checks

## 🛠️ Troubleshooting

### **Common Issues:**

#### **1. Import Errors**
```bash
# Ensure all dependencies are in requirements.txt
pip install -r requirements.txt
```

#### **2. MQTT Connection Issues**
- Check broker credentials in Settings
- Verify TLS configuration
- Test connection with MQTT Explorer first

#### **3. Map Not Loading**
- Verify Mapbox API key in configuration
- Check browser console for errors
- Ensure proper CORS settings

#### **4. Authentication Issues**
- Default admin user is created automatically
- Check database initialization
- Verify user permissions

### **Debug Mode:**
Enable debug logging by setting environment variable:
```bash
STREAMLIT_LOGGER_LEVEL=debug
```

## 📊 Monitoring

### **Health Checks:**
- **Broker Connection**: Status shown in sidebar
- **AGV Count**: Displayed in dashboard header
- **Error Count**: Alert system for issues

### **Logs:**
- Streamlit Community Cloud provides built-in logging
- Check deployment logs for connection issues
- Monitor MQTT client status

## 🔄 Updates

### **Automatic Updates:**
- Push to `main` branch
- GitHub Actions will validate changes
- Streamlit Community Cloud will redeploy automatically

### **Manual Updates:**
1. Make changes to code
2. Commit and push to repository
3. Streamlit Community Cloud will detect changes
4. App will redeploy automatically

## 🎯 Production Checklist

- [ ] **Repository connected** to Streamlit Community Cloud
- [ ] **Main file path** set to `mowbotfleet-dashboard/app.py`
- [ ] **Python version** set to 3.11
- [ ] **Environment variables** configured (if needed)
- [ ] **MQTT broker** configured in Settings
- [ ] **Mapbox API key** configured (if using maps)
- [ ] **Authentication** working (default admin created)
- [ ] **AGV connection** tested
- [ ] **Mission dispatch** tested
- [ ] **Error monitoring** active

## 📞 Support

For deployment issues:
1. Check GitHub Actions logs
2. Review Streamlit Community Cloud logs
3. Verify MQTT broker connectivity
4. Test locally first with `streamlit run app.py`

---

**🎉 Your Mowbot Fleet Dashboard is now live on Streamlit Community Cloud!**
