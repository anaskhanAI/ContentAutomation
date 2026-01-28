"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";

interface ScrapedContent {
  id: string;
  url: string;
  title: string;
  content: string;
  scraped_at: string;
  is_processed: boolean;
  source_id?: string;
  metadata?: {
    source_name?: string;
    keywords?: string[];
  };
}

export default function ActivityPage() {
  const [content, setContent] = useState<ScrapedContent[]>([]);
  const [processingIds, setProcessingIds] = useState<Set<string>>(new Set());
  const [filterProcessed, setFilterProcessed] = useState<string>("all");

  const fetchContent = async () => {
    try {
      const data = await api.getScrapedContent();
      setContent(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Failed to fetch scraped content:", error);
    }
  };

  useEffect(() => {
    fetchContent();
    const interval = setInterval(fetchContent, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSendToOpus = async (contentId: string) => {
    setProcessingIds(prev => new Set(prev).add(contentId));
    try {
      await api.processSingleContent(contentId);
      // Wait a bit then refresh to show updated status
      setTimeout(fetchContent, 2000);
    } catch (error) {
      console.error("Failed to process content:", error);
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(contentId);
        return newSet;
      });
    }
  };

  const contentArray = Array.isArray(content) ? content : [];
  const filteredContent = contentArray.filter(item => {
    if (filterProcessed === "processed") return item.is_processed;
    if (filterProcessed === "unprocessed") return !item.is_processed;
    return true;
  });

  const stats = {
    total: contentArray.length,
    processed: contentArray.filter(c => c.is_processed).length,
    unprocessed: contentArray.filter(c => !c.is_processed).length,
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight gradient-text">Scraped Content</h1>
          <p className="text-muted-foreground font-mono mt-2">View and process individual articles</p>
        </div>
        <div className="flex items-center space-x-2 px-4 py-2 rounded-full glass border-border/40">
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse-slow"></div>
          <span className="text-sm font-mono text-muted-foreground">Auto-refresh: 10s</span>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-3 gap-4">
        <StatMini
          label="Total Articles"
          value={stats.total}
          color="from-primary to-emerald-500"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          }
        />
        <StatMini
          label="Unprocessed"
          value={stats.unprocessed}
          color="from-yellow-500 to-orange-500"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <StatMini
          label="Processed"
          value={stats.processed}
          color="from-primary to-emerald-500"
          icon={
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => setFilterProcessed("all")}
          className={`px-4 py-2 rounded-lg font-mono text-sm transition-smooth ${
            filterProcessed === "all"
              ? "bg-primary text-primary-foreground"
              : "glass hover:bg-secondary/50"
          }`}
        >
          All ({stats.total})
        </button>
        <button
          onClick={() => setFilterProcessed("unprocessed")}
          className={`px-4 py-2 rounded-lg font-mono text-sm transition-smooth ${
            filterProcessed === "unprocessed"
              ? "bg-yellow-500 text-white"
              : "glass hover:bg-secondary/50"
          }`}
        >
          Unprocessed ({stats.unprocessed})
        </button>
        <button
          onClick={() => setFilterProcessed("processed")}
          className={`px-4 py-2 rounded-lg font-mono text-sm transition-smooth ${
            filterProcessed === "processed"
              ? "bg-primary text-primary-foreground"
              : "glass hover:bg-secondary/50"
          }`}
        >
          Processed ({stats.processed})
        </button>
      </div>

      {/* Content List */}
      <div className="space-y-4">
        {filteredContent.length === 0 ? (
          <Card className="glass border-border/40 p-12 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted/50 mb-4">
              <svg className="w-8 h-8 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-muted-foreground font-mono">No scraped content yet</p>
            <p className="text-sm text-muted-foreground font-mono mt-1">Run scraping from the Dashboard to get started</p>
          </Card>
        ) : (
          filteredContent.map((item, index) => (
            <ContentCard
              key={item.id}
              content={item}
              index={index}
              isProcessing={processingIds.has(item.id)}
              onSendToOpus={handleSendToOpus}
            />
          ))
        )}
      </div>
    </div>
  );
}

function ContentCard({
  content,
  index,
  isProcessing,
  onSendToOpus,
}: {
  content: ScrapedContent;
  index: number;
  isProcessing: boolean;
  onSendToOpus: (id: string) => void;
}) {
  const statusConfig = content.is_processed
    ? { color: "bg-primary/10 text-primary border-primary/20", icon: "✓", label: "Processed" }
    : { color: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20", icon: "⏳", label: "Unprocessed" };

  return (
    <Card className="glass border-border/40 p-6 card-hover group">
      <div className="flex items-start space-x-4">
        {/* Timeline Indicator */}
        <div className="flex flex-col items-center">
          <div className={`w-10 h-10 rounded-full ${statusConfig.color} border flex items-center justify-center text-lg font-bold group-hover:scale-110 transition-transform`}>
            {statusConfig.icon}
          </div>
          {index < 49 && <div className="w-0.5 h-8 bg-border/40 mt-2"></div>}
        </div>

        {/* Content */}
        <div className="flex-1 space-y-3">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3">
                <h3 className="font-semibold text-lg">{content.title || "Untitled Article"}</h3>
                <Badge className={`${statusConfig.color} font-mono text-xs`}>
                  {statusConfig.label}
                </Badge>
              </div>
              <a
                href={content.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary hover:underline font-mono mt-1 flex items-center"
              >
                {content.url.substring(0, 60)}...
                <svg className="w-3 h-3 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
            <div className="text-right">
              <p className="text-xs text-muted-foreground font-mono">
                {new Date(content.scraped_at).toLocaleDateString()}
              </p>
              <p className="text-xs text-muted-foreground font-mono">
                {new Date(content.scraped_at).toLocaleTimeString()}
              </p>
            </div>
          </div>

          {/* Metadata */}
          {content.metadata?.source_name && (
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-secondary/50 w-fit">
              <svg className="w-4 h-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <span className="font-mono text-xs">{content.metadata.source_name}</span>
            </div>
          )}

          {/* Content Preview */}
          {content.content && (
            <div className="p-4 rounded-lg bg-secondary/30 border border-border/40">
              <p className="text-sm text-muted-foreground font-mono line-clamp-3">
                {content.content.substring(0, 200)}...
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between pt-2 border-t border-border/40">
            <div className="text-xs text-muted-foreground font-mono">
              ID: {content.id.substring(0, 8)}...
            </div>
            {!content.is_processed && (
              <Button
                onClick={() => onSendToOpus(content.id)}
                disabled={isProcessing}
                size="sm"
                className="bg-primary hover:bg-primary/90 font-semibold group/btn"
              >
                {isProcessing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4 mr-2 group-hover/btn:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Send to Opus
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}

function StatMini({
  label,
  value,
  color,
  icon,
}: {
  label: string;
  value: number;
  color: string;
  icon: React.ReactNode;
}) {
  return (
    <Card className="glass border-border/40 p-4 group hover:scale-105 transition-smooth">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-muted-foreground font-mono mb-1">{label}</p>
          <p className="text-3xl font-bold font-mono gradient-text">{value}</p>
        </div>
        <div className={`p-2.5 rounded-lg bg-gradient-to-br ${color} text-white glow group-hover:glow-strong transition-all`}>
          {icon}
        </div>
      </div>
    </Card>
  );
}
