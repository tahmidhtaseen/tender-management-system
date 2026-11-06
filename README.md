# 🏢 টেন্ডার ম্যানেজমেন্ট সিস্টেম

একটি সম্পূর্ণ ওয়েব-ভিত্তিক টেন্ডার ম্যানেজমেন্ট সিস্টেম যেখানে:
- 🏭 কোম্পানি টেন্ডার পাবলিশ করতে পারে
- 💼 ভেন্ডররা বিড সাবমিট করতে পারে
- 📊 সম্পূর্ণ বিড ম্যানেজমেন্ট সিস্টেম
- 🗄️ MongoDB Atlas দিয়ে পারমানেন্ট ডেটা স্টোরেজ

## ফিচার সমূহ
✅ ইউজার রেজিস্ট্রেশন (কোম্পানি/ভেন্ডর)
✅ টেন্ডার পাবলিশিং
✅ বিড সাবমিশন
✅ বিড ট্র্যাকিং
✅ সুন্দর বাংলা UI
✅ MongoDB Atlas ডেটাবেস
✅ Vercel-ready deployment

## 🚀 Vercel-এ ডিপ্লয়মেন্ট

### ১. MongoDB Atlas সেটআপ করো:
1. https://www.mongodb.com/cloud/atlas/register এ যাও
2. ফ্রি ক্লাস্টার তৈরি করো
3. Database User তৈরি করো (username + password)
4. Network Access-এ `0.0.0.0/0` যোগ করো (সব IP allow)
5. Connection String কপি করো

### ২. Vercel-এ ডিপ্লয় করো:
1. https://vercel.com/new এ যাও
2. এই রিপো Import করো
3. Environment Variables যোগ করো:
   - `MONGODB_URI`: তোমার MongoDB connection string
   - `SECRET_KEY`: যেকোনো random string (যেমন: `my-super-secret-key-12345`)
4. Deploy বাটনে ক্লিক করো!

### ৩. লাইভ URL পাবে:
https://tender-management-system.vercel.app

## লোকালে চালানো
```bash
pip install -r requirements.txt
export MONGODB_URI="your-mongodb-uri"
export SECRET_KEY="your-secret-key"
python api/index.py
```

তারপর ব্রাউজারে যাও: http://127.0.0.1:5000

## 🔒 নিরাপত্তা
- পাসওয়ার্ড হ্যাশ করা হয় (werkzeug.security)
- Session-based authentication
- MongoDB Atlas secure connection
- Environment variables দিয়ে sensitive data protect করা

## 📝 লাইসেন্স
MIT License - ফ্রিতে ব্যবহার করো!
