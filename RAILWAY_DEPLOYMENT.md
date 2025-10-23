# Railway Deployment Guide

## 🚀 Railway Deployment for Mowbot Fleet Dashboard

### **✅ Why Railway is Perfect for Your App:**
- **Always-on** - MQTT connections stay alive 24/7
- **No session timeouts** - real-time updates work continuously
- **Private repositories** - better for proprietary code
- **Dedicated resources** - no sharing with other users
- **Production ready** - perfect for AGV monitoring

## 📋 Prerequisites

- Railway account (free trial at [railway.app](https://railway.app))
- Git repository (can be private)
- MQTT broker credentials

## 🛠️ Deployment Steps

### **Step 1: Create Railway Account**
1. Go to [railway.app](https://railway.app)
2. Click "Login" → "Login with GitHub"
3. Authorize Railway to access your GitHub account

### **Step 2: Deploy from GitHub**
1. In Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your `mowbot_fleet` repository
4. Railway will detect it's a Python app from `requirements.txt`

### **Step 3: Configure Environment Variables**
In Railway dashboard, go to your project → **Variables** tab, add:

```bash
# MQTT Broker Configuration
BROKER_HOST=your-mqtt-broker.com
BROKER_PORT=8883
BROKER_USE_TLS=true
BROKER_USERNAME=your-username
BROKER_PASSWORD=your-password

# Optional: Mapbox API Key
MAPBOX_API_KEY=your-mapbox-api-key

# Streamlit Configuration (optional)
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false
```

### **Step 4: Railway Auto-Deploys**
Railway will automatically:
- Use `railway.json` for start command
- Install dependencies from `requirements.txt`
- Start your Streamlit app with proper configuration
- Provide a public URL

## 🔧 **Railway Configuration Explained**

### **`railway.json` Configuration:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.fileWatcherType none --browser.gatherUsageStats false --client.showErrorDetails false --client.toolbarMode minimal"
  }
}
```

### **Start Command Breakdown:**
- `streamlit run app.py` - Run your Streamlit app
- `--server.port=$PORT` - Use Railway's assigned port
- `--server.address=0.0.0.0` - Allow external access
- `--server.fileWatcherType none` - Disable file watcher (production)
- `--browser.gatherUsageStats false` - Disable telemetry
- `--client.showErrorDetails false` - Hide debug info
- `--client.toolbarMode minimal` - Minimal UI

## 🎯 **Why This Configuration Works:**

### **✅ MQTT Connection Stability:**
- **Always-on** - never sleeps
- **Persistent connections** - MQTT stays alive 24/7
- **Real-time updates** - continuous AGV monitoring

### **✅ Production Optimized:**
- **File watcher disabled** - better for production
- **Telemetry disabled** - privacy focused
- **Minimal UI** - cleaner interface
- **Error details hidden** - professional appearance

## 💰 **Railway Pricing**

### **Free Trial:**
- **$5 credit** for new users
- **Pay-as-you-go** after credits run out
- **Always-on** - never sleeps
- **Perfect for testing** and small deployments

### **Usage Monitoring:**
- **Check credit usage** in Railway dashboard
- **Monitor resource usage** and costs
- **Upgrade to paid** if you exceed credits

## 🚀 **After Deployment:**

### **Your App Will Be Available At:**
- **Public URL**: `https://your-app-name.railway.app`
- **Always accessible** - never sleeps
- **HTTPS enabled** - secure connection
- **Real-time MQTT** - continuous monitoring

### **Access Your App:**
1. **Get URL** from Railway dashboard
2. **Open in browser** - your Streamlit app loads
3. **Login** with admin/admin (default)
4. **Configure MQTT** broker in Settings
5. **Monitor fleet** - real-time updates work 24/7

## 🔍 **Troubleshooting:**

### **If App Won't Start:**
1. **Check Railway logs** for errors
2. **Verify `railway.json`** is in root directory
3. **Check environment** variables are set
4. **Restart app** if needed

### **If MQTT Won't Connect:**
1. **Verify broker credentials** in environment variables
2. **Check broker** is accessible from Railway
3. **Test connection** locally first
4. **Check Railway logs** for connection errors

## 🎯 **Perfect for Your AGV Dashboard:**

### **Why Railway is Ideal:**
- ✅ **MQTT connections** stay alive 24/7
- ✅ **Real-time AGV updates** work continuously
- ✅ **No session timeouts** to interrupt monitoring
- ✅ **Private repository** support for proprietary code
- ✅ **Always-on monitoring** for production use

### **Real-world Benefits:**
- ✅ **AGV status updates** never missed
- ✅ **Mission progress** tracked continuously
- ✅ **Fleet monitoring** works 24/7
- ✅ **Operators get** real-time data instantly

## 🚨 **Important Notes:**

- **Railway free trial** is always-on (no sleep)
- **Perfect for MQTT applications** that need persistent connections
- **$5 trial credit** is usually sufficient for testing
- **Private repositories** are fully supported
- **Better performance** than shared hosting platforms

Railway is the perfect choice for your real-time MQTT dashboard! 🚀✨
