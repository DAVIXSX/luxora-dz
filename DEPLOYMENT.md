# Deployment Guide: Luxora DZ on Render

This guide will help you deploy your Luxora DZ e-commerce application to Render.

## 📋 Prerequisites

- GitHub account with your Luxora DZ repository
- Render account (free tier available)
- Your app should be pushed to GitHub

## 🚀 Deployment Steps

### Method 1: Automatic Deployment (Recommended)

1. **Connect to Render**
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" → "Web Service"
   - Connect your GitHub account if not already connected
   - Select your `luxora-dz` repository

2. **Configure Service**
   - **Name**: `luxora-dz` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn --config gunicorn.conf.py app:app`

3. **Set Environment Variables**
   Go to the "Environment" section and add these variables:
   
   ```
   SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
   FLASK_ENV=production
   FLASK_DEBUG=False
   ADMIN_USERNAME=your_admin_username
   ADMIN_PASSWORD=your_strong_password_123
   PYTHON_VERSION=3.11.7
   ```

   **⚠️ IMPORTANT**: 
   - Generate a strong `SECRET_KEY` using: `python -c "import secrets; print(secrets.token_hex(32))"`
   - Use a strong password for `ADMIN_PASSWORD`
   - Never use the default values in production

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - The build process takes 2-5 minutes

### Method 2: Using render.yaml (Alternative)

If you prefer Infrastructure as Code:

1. The repository already includes a `render.yaml` file
2. Go to Render dashboard → "New +" → "Blueprint"
3. Connect your GitHub repo
4. Render will read the `render.yaml` configuration automatically
5. You'll still need to set the environment variables manually

## 🔧 Configuration Details

### Environment Variables Explained

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | `a1b2c3d4e5f6...` (64+ characters) |
| `FLASK_ENV` | Environment mode | `production` |
| `FLASK_DEBUG` | Debug mode (NEVER true in production) | `False` |
| `ADMIN_USERNAME` | Your admin panel username | `admin_user` |
| `ADMIN_PASSWORD` | Your admin panel password | `MySecurePass123!` |
| `PYTHON_VERSION` | Python version to use | `3.11.7` |

### Build Configuration

- **Build Command**: `./build.sh`
  - Installs dependencies
  - Creates upload directories
  - Initializes database tables
  
- **Start Command**: `gunicorn --config gunicorn.conf.py app:app`
  - Uses Gunicorn WSGI server
  - Configured for production performance
  - Handles multiple workers

## 🎯 Post-Deployment

### 1. Verify Deployment
- Your app will be available at: `https://your-service-name.onrender.com`
- Test the homepage loads correctly
- Verify static files (CSS, images) are working

### 2. Admin Access
- Go to: `https://your-service-name.onrender.com/login`
- Use your `ADMIN_USERNAME` and `ADMIN_PASSWORD`
- Verify you can access the admin panel at `/admin`

### 3. Test Core Functionality
- ✅ Browse products
- ✅ Place a test order
- ✅ Admin can view orders
- ✅ Admin can add products
- ✅ Image uploads work

## 📊 Free Tier Limitations

Render's free tier includes:
- ✅ 512MB RAM
- ✅ Shared CPU
- ✅ 100GB bandwidth/month
- ✅ Custom domains
- ⚠️ Apps sleep after 15 minutes of inactivity
- ⚠️ Cold starts when waking up (~30 seconds)

## 🔄 Updates and Redeployment

### Automatic Deployments
- Push changes to your `main` branch on GitHub
- Render automatically detects changes and rebuilds
- No manual intervention needed

### Manual Deployment
- Go to your service in Render dashboard
- Click "Manual Deploy" → "Deploy latest commit"

## 🛠️ Troubleshooting

### Build Failures

1. **Python Dependencies Error**
   ```bash
   # Check requirements.txt format
   # Ensure all dependencies have proper versions
   ```

2. **Permission Issues**
   ```bash
   # Make sure build.sh is executable
   chmod +x build.sh
   ```

### Runtime Issues

1. **App Won't Start**
   - Check environment variables are set correctly
   - Verify `SECRET_KEY` is not empty
   - Check Render logs for detailed error messages

2. **Database Issues**
   - SQLite database is created automatically
   - Check if upload directory exists
   - Verify database permissions

3. **Static Files Not Loading**
   - Ensure `static/` directory structure is correct
   - Check if CSS/JS files are being served properly

### Checking Logs
- Go to Render Dashboard → Your Service → "Logs"
- Look for error messages and stack traces
- Use logs to debug issues

## 💰 Upgrading to Paid Plan

For production traffic, consider upgrading:
- **Starter Plan ($7/month)**:
  - No sleeping
  - Faster builds
  - Priority support
  
- **Standard Plan ($25/month)**:
  - More resources
  - Better performance
  - Advanced features

## 🔒 Security Considerations

1. **Environment Variables**
   - Never commit `.env` files to GitHub
   - Use Render's environment variable interface
   - Regularly rotate secrets

2. **Admin Access**
   - Use strong passwords
   - Consider IP whitelisting for admin routes (custom implementation)
   - Monitor admin access logs

3. **Database**
   - Regular backups (manual for SQLite)
   - Monitor for unusual activity
   - Keep software updated

## 📞 Support

- **Render Support**: [render.com/docs](https://render.com/docs)
- **Flask Documentation**: [flask.palletsprojects.com](https://flask.palletsprojects.com)
- **Project Issues**: Open an issue on your GitHub repository

---

🎉 **Congratulations!** Your Luxora DZ e-commerce platform is now live on Render!
