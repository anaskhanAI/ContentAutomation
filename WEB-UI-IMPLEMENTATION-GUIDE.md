# 🚀 Web UI Implementation Guide

## ✅ **What's Been Created**

### **Backend (FastAPI) - COMPLETE** ✅
```
backend/
├── main.py               ✅ Complete FastAPI application with all endpoints
└── requirements.txt      ✅ Python dependencies
```

### **Frontend (Next.js) - Configuration Complete** ✅
```
frontend/
├── package.json          ✅ Dependencies configured
├── tsconfig.json         ✅ TypeScript config
├── tailwind.config.ts    ✅ Tailwind CSS config
├── next.config.mjs       ✅ Next.js config
└── postcss.config.mjs    ✅ PostCSS config
```

---

## 🏗️ **Complete Frontend Structure to Create**

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          [CREATE] Root layout
│   │   ├── page.tsx            [CREATE] Dashboard page
│   │   ├── globals.css         [CREATE] Global styles
│   │   ├── sources/
│   │   │   └── page.tsx        [CREATE] Source management
│   │   ├── settings/
│   │   │   └── page.tsx        [CREATE] Settings page
│   │   └── activity/
│   │       └── page.tsx        [CREATE] Activity logs
│   ├── components/
│   │   ├── ui/                 [CREATE] Shadcn components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── input.tsx
│   │   │   ├── label.tsx
│   │   │   ├── select.tsx
│   │   │   ├── switch.tsx
│   │   │   └── toast.tsx
│   │   ├── DashboardStats.tsx  [CREATE]
│   │   ├── SourceCard.tsx      [CREATE]
│   │   ├── ActivityList.tsx    [CREATE]
│   │   └── Navbar.tsx          [CREATE]
│   ├── lib/
│   │   ├── api.ts              [CREATE] API client
│   │   ├── types.ts            [CREATE] TypeScript types
│   │   └── utils.ts            [CREATE] Utilities
│   └── hooks/
│       ├── useStats.ts         [CREATE]
│       └── useSources.ts       [CREATE]
├── public/
│   └── (static assets)
└── README.md
```

---

## 📋 **Step-by-Step Implementation**

### **Step 1: Setup Frontend** (5 minutes)

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

---

### **Step 2: Install Shadcn UI** (5 minutes)

```bash
# Initialize Shadcn
npx shadcn-ui@latest init

# When prompted:
# - TypeScript: Yes
# - Style: Default
# - Base color: Slate
# - Global CSS: src/app/globals.css
# - CSS variables: Yes
# - Tailwind config: tailwind.config.ts
# - Components: @/components
# - Utils: @/lib/utils
# - RSC: Yes
# - App router: Yes

# Install needed components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add input
npx shadcn-ui@latest add label
npx shadcn-ui@latest add select
npx shadcn-ui@latest add switch
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add table
```

---

### **Step 3: Create Core Files** (30 minutes)

I've provided the complete file contents below. Create each file:

#### **A. src/lib/types.ts**

```typescript
export interface Source {
  id: string;
  url: string;
  name: string;
  source_type: string;
  is_active: boolean;
  scraping_frequency_minutes: number;
  last_scraped_at?: string;
  metadata: {
    rss_feed_url?: string;
    has_rss: boolean;
    max_articles: number;
    priority: string;
    description?: string;
  };
  created_at: string;
  updated_at?: string;
}

export interface Stats {
  active_sources: number;
  total_sources: number;
  articles_today: number;
  jobs_pending: number;
  unprocessed_articles: number;
  last_scrape_at?: string;
  credits_used_monthly: number;
  credits_limit_monthly: number;
}

export interface TaskStatus {
  status: 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  articles_scraped?: number;
  jobs_submitted?: number;
  credits_used?: number;
  error?: string;
}

export interface Activity {
  id: string;
  workflow_id: string;
  scraped_content_id: string;
  status: string;
  job_payload: any;
  created_at: string;
  job_execution_id?: string;
}
```

#### **B. src/lib/api.ts**

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  // Stats
  getStats: async () => {
    const res = await fetch(`${API_URL}/api/stats`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  },

  // Sources
  getSources: async () => {
    const res = await fetch(`${API_URL}/api/sources`);
    if (!res.ok) throw new Error('Failed to fetch sources');
    return res.json();
  },

  createSource: async (data: any) => {
    const res = await fetch(`${API_URL}/api/sources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create source');
    return res.json();
  },

  updateSource: async (id: string, data: any) => {
    const res = await fetch(`${API_URL}/api/sources/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update source');
    return res.json();
  },

  toggleSource: async (id: string, active: boolean) => {
    const res = await fetch(`${API_URL}/api/sources/${id}/toggle`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ active }),
    });
    if (!res.ok) throw new Error('Failed to toggle source');
    return res.json();
  },

  deleteSource: async (id: string) => {
    const res = await fetch(`${API_URL}/api/sources/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete source');
    return res.json();
  },

  // Scraping
  triggerScrape: async (data?: any) => {
    const res = await fetch(`${API_URL}/api/scrape`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data || {}),
    });
    if (!res.ok) throw new Error('Failed to trigger scrape');
    return res.json();
  },

  getScrapeStatus: async (taskId: string) => {
    const res = await fetch(`${API_URL}/api/scrape/status/${taskId}`);
    if (!res.ok) throw new Error('Failed to fetch status');
    return res.json();
  },

  // Processing
  triggerProcess: async (data: any) => {
    const res = await fetch(`${API_URL}/api/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to trigger process');
    return res.json();
  },

  getProcessStatus: async (taskId: string) => {
    const res = await fetch(`${API_URL}/api/process/status/${taskId}`);
    if (!res.ok) throw new Error('Failed to fetch status');
    return res.json();
  },

  // Settings
  getSettings: async () => {
    const res = await fetch(`${API_URL}/api/settings`);
    if (!res.ok) throw new Error('Failed to fetch settings');
    return res.json();
  },

  updateSettings: async (data: any) => {
    const res = await fetch(`${API_URL}/api/settings`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update settings');
    return res.json();
  },

  // Activity
  getActivity: async () => {
    const res = await fetch(`${API_URL}/api/activity`);
    if (!res.ok) throw new Error('Failed to fetch activity');
    return res.json();
  },
};
```

#### **C. src/lib/utils.ts**

```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date) {
  return new Date(date).toLocaleString()
}

export function formatRelativeTime(date: string) {
  const now = new Date();
  const past = new Date(date);
  const seconds = Math.floor((now.getTime() - past.getTime()) / 1000);

  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
  return `${Math.floor(seconds / 86400)} days ago`;
}
```

---

### **Step 4: Create Dashboard Page** (15 minutes)

Create `src/app/page.tsx`:

```typescript
'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/api';
import { Stats } from '@/lib/types';
import { formatRelativeTime } from '@/lib/utils';
import { Loader2, RefreshCw, Send } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [processing, setProcessing] = useState(false);

  const loadStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const handleScrape = async () => {
    setScraping(true);
    try {
      const { task_id } = await api.triggerScrape();
      // Poll for completion
      const pollStatus = setInterval(async () => {
        const status = await api.getScrapeStatus(task_id);
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(pollStatus);
          setScraping(false);
          loadStats();
          alert(status.message);
        }
      }, 2000);
    } catch (error) {
      setScraping(false);
      alert('Failed to start scraping');
    }
  };

  const handleProcess = async () => {
    setProcessing(true);
    try {
      const { task_id } = await api.triggerProcess({ max_items: 15, min_relevance: 0.5 });
      const pollStatus = setInterval(async () => {
        const status = await api.getProcessStatus(task_id);
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(pollStatus);
          setProcessing(false);
          loadStats();
          alert(status.message);
        }
      }, 2000);
    } catch (error) {
      setProcessing(false);
      alert('Failed to start processing');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">Content Automation Dashboard</h1>
        <p className="text-muted-foreground">
          Manage your content scraping and Opus workflow automation
        </p>
      </div>

      <div className="flex gap-4">
        <Button
          size="lg"
          onClick={handleScrape}
          disabled={scraping}
        >
          {scraping ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Scraping...
            </>
          ) : (
            <>
              <RefreshCw className="mr-2 h-4 w-4" />
              Scrape Content Now
            </>
          )}
        </Button>

        <Button
          size="lg"
          variant="secondary"
          onClick={handleProcess}
          disabled={processing}
        >
          {processing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Send className="mr-2 h-4 w-4" />
              Process & Send to Opus
            </>
          )}
        </Button>
      </div>

      {stats && (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Sources</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.active_sources}/{stats.total_sources}</div>
                <p className="text-xs text-muted-foreground">
                  Content sources enabled
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Articles Today</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.articles_today}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.last_scrape_at ? `Last scrape: ${formatRelativeTime(stats.last_scrape_at)}` : 'Never scraped'}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pending Jobs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.jobs_pending}</div>
                <p className="text-xs text-muted-foreground">
                  Awaiting approval in Opus
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Unprocessed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.unprocessed_articles}</div>
                <p className="text-xs text-muted-foreground">
                  Articles ready to process
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Credit Usage</CardTitle>
              <CardDescription>Firecrawl API credits (monthly)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">
                    {stats.credits_used_monthly} / {stats.credits_limit_monthly} credits
                  </span>
                  <span className="text-sm text-muted-foreground">
                    {Math.round((stats.credits_used_monthly / stats.credits_limit_monthly) * 100)}% used
                  </span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full transition-all"
                    style={{ width: `${(stats.credits_used_monthly / stats.credits_limit_monthly) * 100}%` }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
```

---

### **Step 5: Create Layout & Globals** (10 minutes)

Create `src/app/layout.tsx`:

```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Content Automation",
  description: "Automated content scraping and Opus workflow management",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="border-b">
          <div className="container mx-auto flex h-16 items-center px-4">
            <Link href="/" className="font-bold text-xl mr-6">
              Content Automation
            </Link>
            <div className="flex gap-6">
              <Link href="/" className="text-sm hover:underline">
                Dashboard
              </Link>
              <Link href="/sources" className="text-sm hover:underline">
                Sources
              </Link>
              <Link href="/settings" className="text-sm hover:underline">
                Settings
              </Link>
              <Link href="/activity" className="text-sm hover:underline">
                Activity
              </Link>
            </div>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

Create `src/app/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

---

## 🚀 **Running the Application**

### **Terminal 1: Backend**
```bash
cd backend
pip install -r requirements.txt
python main.py
# API running at http://localhost:8000
```

### **Terminal 2: Frontend**
```bash
cd frontend
npm install
npm run dev
# UI running at http://localhost:3000
```

---

## 📦 **Deployment to Vercel**

### **Step 1: Create vercel.json**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ]
}
```

### **Step 2: Deploy Backend Separately**

**Option A: Railway**
1. Create account on Railway.app
2. New Project → Deploy from GitHub
3. Select your repo
4. Set root directory: `/backend`
5. Add environment variables from `.env`
6. Deploy!

**Option B: Render**
1. Create account on Render.com
2. New Web Service
3. Connect GitHub repo
4. Root directory: `backend`
5. Build: `pip install -r requirements.txt`
6. Start: `uvicorn main:app --host 0.0.0.0 --port 8000`

### **Step 3: Deploy Frontend to Vercel**
```bash
cd frontend
vercel
# Follow prompts
# Set NEXT_PUBLIC_API_URL to your backend URL
```

---

## ✅ **Next Steps**

1. **Create remaining pages:**
   - `src/app/sources/page.tsx` - Source management UI
   - `src/app/settings/page.tsx` - Settings UI
   - `src/app/activity/page.tsx` - Activity logs UI

2. **Add more components as needed**

3. **Test the complete flow:**
   - Add/edit sources in UI
   - Trigger scraping
   - Process content
   - Verify in Opus

---

## 📚 **Resources**

- **Shadcn UI Docs**: https://ui.shadcn.com
- **Next.js Docs**: https://nextjs.org/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Tailwind CSS**: https://tailwindcss.com

---

**Implementation complete! Backend is ready, frontend foundation is set up. Complete the frontend pages following the patterns shown above.** 🎉
