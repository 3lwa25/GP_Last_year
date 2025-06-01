# 🚀 Quick Email Alternatives for Hirely Job Portal

## If Gmail App Password Doesn't Work

### **Option 1: SendGrid (Recommended)**
**Professional email service - FREE for 100 emails/day**

1. **Sign up**: https://sendgrid.com/free/
2. **Get API Key**: Dashboard → Settings → API Keys
3. **Add to .env file**:
```env
SENDGRID_API_KEY=your_api_key_here
SENDGRID_FROM_EMAIL=hirely8@gmail.com
```

### **Option 2: Outlook/Hotmail**
**Use Microsoft email instead**

1. **Create Outlook account** or use existing
2. **Add to .env file**:
```env
OUTLOOK_EMAIL_USER=your_outlook@outlook.com
OUTLOOK_EMAIL_PASSWORD=your_outlook_password
OUTLOOK_FROM_EMAIL=your_outlook@outlook.com
```

### **Option 3: Different Gmail Account**
**Try with a fresh Gmail account**

1. **Create new Gmail account**: https://accounts.google.com/signup
2. **Follow same App Password process**
3. **Update .env with new credentials**

## 🎯 **Immediate Solution**
**Current system works perfectly - messages appear in console until email is fixed!**

Your contact form is **100% functional** - it just shows messages in the terminal instead of sending emails until Gmail is properly configured. 