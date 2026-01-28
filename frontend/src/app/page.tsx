"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { Stats, TaskStatus } from "@/lib/types";

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [isScraping, setIsScraping] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [scrapeTaskId, setScrapeTaskId] = useState<string | null>(null);
  const [processTaskId, setProcessTaskId] = useState<string | null>(null);

  // Fetch stats
  const fetchStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  // Poll task status
  useEffect(() => {
    if (!scrapeTaskId && !processTaskId) return;

    const pollInterval = setInterval(async () => {
      if (scrapeTaskId) {
        try {
          const status: TaskStatus = await api.getScrapeStatus(scrapeTaskId);
          if (status.status === "completed" || status.status === "failed" || status.status === "cancelled") {
            setIsScraping(false);
            setScrapeTaskId(null);
            fetchStats();
          }
        } catch (error) {
          console.error("Failed to poll scrape status:", error);
        }
      }

      if (processTaskId) {
        try {
          const status: TaskStatus = await api.getProcessStatus(processTaskId);
          if (status.status === "completed" || status.status === "failed" || status.status === "cancelled") {
            setIsProcessing(false);
            setProcessTaskId(null);
            fetchStats();
          }
        } catch (error) {
          console.error("Failed to poll process status:", error);
        }
      }
    }, 3000);

    return () => clearInterval(pollInterval);
  }, [scrapeTaskId, processTaskId]);

  const handleScrape = async () => {
    setIsScraping(true);
    try {
      const result = await api.triggerScrape();
      setScrapeTaskId(result.task_id);
    } catch (error) {
      console.error("Scrape failed:", error);
      setIsScraping(false);
    }
  };

  const handleStopScrape = async () => {
    if (!scrapeTaskId) return;
    try {
      await api.cancelTask(scrapeTaskId);
      setIsScraping(false);
      setScrapeTaskId(null);
    } catch (error) {
      console.error("Failed to stop scraping:", error);
    }
  };

  const handleProcess = async () => {
    setIsProcessing(true);
    try {
      const result = await api.triggerProcess({ max_items: 15, min_relevance: 0.5 });
      setProcessTaskId(result.task_id);
    } catch (error) {
      console.error("Process failed:", error);
      setIsProcessing(false);
    }
  };

  const handleStopProcess = async () => {
    if (!processTaskId) return;
    try {
      await api.cancelTask(processTaskId);
      setIsProcessing(false);
      setProcessTaskId(null);
    } catch (error) {
      console.error("Failed to stop processing:", error);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight gradient-text">Dashboard</h1>
        <p className="text-muted-foreground font-mono mt-2">Monitor and control your content automation</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Sources"
          value={stats?.active_sources ?? 0}
          icon={
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          }
          color="from-primary to-emerald-500"
        />

        <StatCard
          title="Articles Today"
          value={stats?.articles_scraped_today ?? 0}
          icon={
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          }
          color="from-blue-500 to-cyan-500"
        />

        <StatCard
          title="Pending Jobs"
          value={stats?.pending_jobs ?? 0}
          icon={
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
          color="from-yellow-500 to-orange-500"
        />

        <StatCard
          title="Unprocessed"
          value={stats?.unprocessed_articles ?? 0}
          icon={
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
          }
          color="from-purple-500 to-pink-500"
        />
      </div>

      {/* Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Scraping */}
        <Card className="glass border-border/40 p-6">
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Content Scraping
          </h3>
          <p className="text-sm text-muted-foreground font-mono mb-4">
            Scrape fresh content from all active sources
          </p>
          <div className="flex items-center space-x-3">
            {!isScraping ? (
              <Button
                onClick={handleScrape}
                size="lg"
                className="flex-1 glass bg-primary/10 hover:bg-primary/20 border-primary/20 text-primary font-semibold group"
              >
                <svg className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Start Scraping
              </Button>
            ) : (
              <>
                <Button
                  disabled
                  size="lg"
                  className="flex-1 glass bg-primary/10 border-primary/20 text-primary font-semibold"
                >
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
                  Scraping...
                </Button>
                <Button
                  onClick={handleStopScrape}
                  size="lg"
                  variant="destructive"
                  className="font-semibold group"
                >
                  <svg className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  Stop
                </Button>
              </>
            )}
          </div>
        </Card>

        {/* Processing */}
        <Card className="glass border-border/40 p-6">
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Process & Send to Opus
          </h3>
          <p className="text-sm text-muted-foreground font-mono mb-4">
            Process unprocessed content and submit to Opus
          </p>
          <div className="flex items-center space-x-3">
            {!isProcessing ? (
              <Button
                onClick={handleProcess}
                size="lg"
                className="flex-1 glass bg-blue-500/10 hover:bg-blue-500/20 border-blue-500/20 text-blue-400 font-semibold group"
              >
                <svg className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Start Processing
              </Button>
            ) : (
              <>
                <Button
                  disabled
                  size="lg"
                  className="flex-1 glass bg-blue-500/10 border-blue-500/20 text-blue-400 font-semibold"
                >
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
                  Processing...
                </Button>
                <Button
                  onClick={handleStopProcess}
                  size="lg"
                  variant="destructive"
                  className="font-semibold group"
                >
                  <svg className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  Stop
                </Button>
              </>
            )}
          </div>
        </Card>
      </div>

      {/* System Info */}
      <Card className="glass border-border/40 p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <svg className="w-5 h-5 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          System Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex justify-between items-center py-2 px-3 rounded-lg bg-secondary/30">
            <span className="text-sm font-medium font-mono">Total Sources</span>
            <span className="font-semibold font-mono">{stats?.total_sources ?? 0}</span>
          </div>
          <div className="flex justify-between items-center py-2 px-3 rounded-lg bg-secondary/30">
            <span className="text-sm font-medium font-mono">Articles Today</span>
            <span className="font-semibold font-mono text-primary">{stats?.articles_scraped_today ?? 0}</span>
          </div>
          <div className="flex justify-between items-center py-2 px-3 rounded-lg bg-secondary/30">
            <span className="text-sm font-medium font-mono">Last Scrape</span>
            <span className="font-semibold font-mono text-xs">
              {stats?.last_scrape_time ? new Date(stats.last_scrape_time).toLocaleString() : "Never"}
            </span>
          </div>
          <div className="flex justify-between items-center py-2 px-3 rounded-lg bg-secondary/30">
            <span className="text-sm font-medium font-mono">Status</span>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse-slow"></div>
              <span className="font-semibold font-mono text-xs text-primary">Operational</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}

function StatCard({ title, value, icon, color }: { title: string; value: number; icon: React.ReactNode; color: string }) {
  return (
    <Card className="glass border-border/40 p-6 card-hover group">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground font-medium">{title}</p>
          <p className="text-4xl font-bold font-mono">{value}</p>
        </div>
        <div className={`p-3 rounded-xl bg-gradient-to-br ${color} text-white glow group-hover:glow-strong transition-all`}>
          {icon}
        </div>
      </div>
    </Card>
  );
}
