# 🌤️ Real-Time Weather Setup Guide

## Quick Start (No API Key Needed!)

The app works **perfectly fine without an API key**! It will use mock/sample data for real-time weather.

However, for **actual live weather data**, follow these simple steps:

---

## Step 1: Get Your Free API Key

1. **Sign up** at OpenWeatherMap:
   👉 https://openweathermap.org/api

2. **Click "Sign Up"** (top right)

3. **Fill in details**:
   - Email
   - Password
   - Agree to terms

4. **Verify email** (check inbox)

5. **Generate API Key**:
   - Go to: https://home.openweathermap.org/api_keys
   - Copy the "Default" API key (or create new one)
   - It looks like: `abcd1234efgh5678ijkl90mnopqrstuv`

---

## Step 2: Add API Key to Your Project

### Option A: Using `.env` file (Recommended)

1. **Create a file** named `.env` in your project root:
   ```
   WEATHER_FORECASTING/
   └── .env  ← Create this file
   ```

2. **Add this line** to `.env`:
   ```
   OPENWEATHERMAP_API_KEY=paste_your_api_key_here
   ```
   
   Example:
   ```
   OPENWEATHERMAP_API_KEY=abcd1234efgh5678ijkl90mnopqrstuv
   ```

3. **Save the file**

4. **Restart the Streamlit app**

### Option B: Using Streamlit Secrets (For Deployment)

1. **Create** `.streamlit/secrets.toml`

2. **Add**:
   ```toml
   OPENWEATHERMAP_API_KEY = "paste_your_api_key_here"
   ```

---

## Step 3: Verify It's Working

1. **Restart your app**:
   ```powershell
   streamlit run app.py
   ```

2. **Go to Dashboard**

3. **Select any city**

4. **Check if temperature looks realistic** (not random numbers)

5. **Look for** the ☁️ emoji and weather description

---

## Free Tier Limits

✅ **1,000 API calls per day**  
✅ **60 calls per minute**  
✅ **More than enough for personal use!**

**Our app caches data for 30 minutes**, so you'll only use ~50 calls/day even with frequent refreshes.

---

## Troubleshooting

### "Invalid API key"
- Check for typos in `.env`
- Ensure no spaces before/after the key
- Wait 10 minutes after creating key (activation time)

### "API key not found"
- Make sure `.env` is in the project root (same level as `app.py`)
- Restart Streamlit after creating `.env`

### Still seeing mock data?
- Run this test:
  ```powershell
  .\env\Scripts\python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENWEATHERMAP_API_KEY'))"
  ```
  It should print your API key.

---

## Security Note

⚠️ **Never commit `.env` to Git!**

It's already in `.gitignore`, but double-check:
```bash
git status
# .env should NOT appear in the list
```

---

## Alternative: Run Without API Key

The app is **fully functional without an API key**!

It will show:
- ✅ 30-day historical data (real data from Meteostat)
- ✅ Temperature trends & charts (real data)
- ⚠️ Current weather (simulated/mock data)

**Use case**: Great for testing, development, or learning without signup!

---

*Last Updated: 2026-02-07*
