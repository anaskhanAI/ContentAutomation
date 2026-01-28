# Content Automation Frontend

Modern web UI for managing content scraping and Opus workflows

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Backend API running (see `../backend/README.md`)

### Setup

```bash
# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 🎨 Tech Stack

- **Next.js 14** - React framework (App Router)
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Shadcn UI** - Component library
- **Lucide React** - Icons

---

## 📁 Project Structure

```
src/
├── app/
│   ├── page.tsx           # Dashboard
│   ├── sources/page.tsx   # Source management
│   ├── settings/page.tsx  # Settings
│   └── activity/page.tsx  # Activity logs
├── components/ui/         # Shadcn components
├── lib/
│   ├── api.ts            # API client
│   ├── types.ts          # TypeScript types
│   └── utils.ts          # Utilities
└── hooks/                 # Custom React hooks
```

---

## 🛠️ Development

### Install Shadcn Components

```bash
# Initialize (if not done)
npx shadcn-ui@latest init

# Add components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add input
npx shadcn-ui@latest add label
npx shadcn-ui@latest add select
npx shadcn-ui@latest add switch
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add badge
```

### Build for Production

```bash
npm run build
npm start
```

---

## 🚢 Deployment to Vercel

### Option 1: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL
# Enter your backend API URL (e.g., https://api.railway.app)
```

### Option 2: GitHub Integration

1. Push to GitHub
2. Go to vercel.com
3. Import Project
4. Select repository
5. **Settings:**
   - Framework: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`
6. **Environment Variables:**
   - `NEXT_PUBLIC_API_URL` = Your backend URL
7. Deploy!

---

## 🔧 Configuration

### API URL

**Development:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Production:**
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

---

## ✨ Features

### Dashboard
- Real-time stats
- Quick action buttons (Scrape, Process)
- Credit usage visualization
- Last scrape timestamp

### Sources
- Add/edit/delete sources
- Toggle active/inactive
- Configure articles per source
- Set priority levels
- View RSS status

### Settings
- Scraping configuration
- Processing parameters
- Credit optimization
- Daily limits

### Activity
- Recent Opus jobs
- Job status tracking
- Created timestamps
- Source attribution

---

## 🐛 Troubleshooting

### API Connection Failed

**Check:**
1. Backend is running (`http://localhost:8000`)
2. CORS is enabled in backend
3. `NEXT_PUBLIC_API_URL` is correct in `.env.local`

### Components Not Found

```bash
# Reinstall Shadcn components
npx shadcn-ui@latest add button card dialog
```

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

---

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Shadcn UI](https://ui.shadcn.com)
- [Tailwind CSS](https://tailwindcss.com)
