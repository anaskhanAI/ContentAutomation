"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { api } from "@/lib/api";

interface Settings {
  max_articles_per_source: number;
  max_crawl_pages: number;
  rss_freshness_days: number;
  max_items_per_run: number;
  daily_job_limit: number;
  min_relevance_score: number;
  use_rss: boolean;
  deduplicate_urls: boolean;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  const fetchSettings = async () => {
    try {
      const data = await api.getSettings();
      setSettings(data);
    } catch (error) {
      console.error("Failed to fetch settings:", error);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async () => {
    if (!settings) return;
    setIsSaving(true);
    setSaveMessage("");
    try {
      await api.updateSettings(settings);
      setSaveMessage("Settings saved successfully!");
      setTimeout(() => setSaveMessage(""), 3000);
    } catch (error) {
      console.error("Failed to save settings:", error);
      setSaveMessage("Failed to save settings");
    } finally {
      setIsSaving(false);
    }
  };

  if (!settings) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight gradient-text">Settings</h1>
        <p className="text-muted-foreground font-mono mt-2">Configure scraping and processing parameters</p>
      </div>

      {/* Settings Sections */}
      <div className="space-y-6">
        {/* Scraping Settings */}
        <Card className="glass border-border/40 p-6">
          <h2 className="text-2xl font-semibold mb-6 flex items-center">
            <div className="w-1.5 h-8 bg-gradient-to-b from-primary to-emerald-500 rounded-full mr-3"></div>
            Scraping Configuration
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <SettingInput
              label="Max Articles Per Source"
              description="Maximum articles to scrape from each source"
              value={settings.max_articles_per_source}
              onChange={(v) => setSettings({ ...settings, max_articles_per_source: v })}
              min={1}
              max={10}
              icon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              }
            />
            <SettingInput
              label="Max Crawl Pages"
              description="Maximum pages to crawl per website"
              value={settings.max_crawl_pages}
              onChange={(v) => setSettings({ ...settings, max_crawl_pages: v })}
              min={1}
              max={10}
              icon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              }
            />
            <SettingInput
              label="RSS Freshness Days"
              description="Only fetch articles from last N days"
              value={settings.rss_freshness_days}
              onChange={(v) => setSettings({ ...settings, rss_freshness_days: v })}
              min={1}
              max={30}
              icon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 5c7.18 0 13 5.82 13 13M6 11a7 7 0 017 7m-6 0a1 1 0 11-2 0 1 1 0 012 0z" />
                </svg>
              }
            />
            <SettingInput
              label="Max Items Per Run"
              description="Maximum items to process in one run"
              value={settings.max_items_per_run}
              onChange={(v) => setSettings({ ...settings, max_items_per_run: v })}
              min={1}
              max={50}
              icon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              }
            />
          </div>
        </Card>

        {/* Processing Settings */}
        <Card className="glass border-border/40 p-6">
          <h2 className="text-2xl font-semibold mb-6 flex items-center">
            <div className="w-1.5 h-8 bg-gradient-to-b from-blue-500 to-cyan-500 rounded-full mr-3"></div>
            Processing Configuration
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <SettingInput
              label="Daily Job Limit"
              description="Maximum Opus jobs per day"
              value={settings.daily_job_limit}
              onChange={(v) => setSettings({ ...settings, daily_job_limit: v })}
              min={1}
              max={100}
              icon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              }
            />
            <SettingInput
              label="Min Relevance Score"
              description="Minimum score to process content (0-1)"
              value={settings.min_relevance_score}
              onChange={(v) => setSettings({ ...settings, min_relevance_score: v })}
              min={0}
              max={1}
              step={0.1}
              icon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              }
            />
          </div>
        </Card>

        {/* Feature Toggles */}
        <Card className="glass border-border/40 p-6">
          <h2 className="text-2xl font-semibold mb-6 flex items-center">
            <div className="w-1.5 h-8 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full mr-3"></div>
            Feature Toggles
          </h2>
          <div className="space-y-6">
            <SettingToggle
              label="Use RSS Feeds"
              description="Prioritize RSS feeds for faster, fresher content"
              checked={settings.use_rss}
              onCheckedChange={(v) => setSettings({ ...settings, use_rss: v })}
              icon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 5c7.18 0 13 5.82 13 13M6 11a7 7 0 017 7m-6 0a1 1 0 11-2 0 1 1 0 012 0z" />
                </svg>
              }
            />
            <SettingToggle
              label="Deduplicate URLs"
              description="Skip already scraped URLs to save credits"
              checked={settings.deduplicate_urls}
              onCheckedChange={(v) => setSettings({ ...settings, deduplicate_urls: v })}
              icon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            />
          </div>
        </Card>

        {/* Save Button */}
        <div className="flex items-center justify-between">
          <div className="flex-1">
            {saveMessage && (
              <p className={`text-sm font-mono ${saveMessage.includes("success") ? "text-primary" : "text-destructive"}`}>
                {saveMessage}
              </p>
            )}
          </div>
          <Button
            onClick={handleSave}
            disabled={isSaving}
            size="lg"
            className="bg-primary hover:bg-primary/90 font-semibold px-8"
          >
            {isSaving ? (
              <>
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2"></div>
                Saving...
              </>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Save Settings
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

function SettingInput({
  label,
  description,
  value,
  onChange,
  min,
  max,
  step = 1,
  icon,
}: {
  label: string;
  description: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
  icon: React.ReactNode;
}) {
  return (
    <div className="space-y-3">
      <div className="flex items-start space-x-3">
        <div className="p-2 rounded-lg bg-primary/10 text-primary mt-1">
          {icon}
        </div>
        <div className="flex-1">
          <Label htmlFor={label} className="text-sm font-semibold">{label}</Label>
          <p className="text-xs text-muted-foreground font-mono mt-1">{description}</p>
        </div>
      </div>
      <Input
        id={label}
        type="number"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        min={min}
        max={max}
        step={step}
        className="glass border-border/40 font-mono text-lg font-semibold"
      />
    </div>
  );
}

function SettingToggle({
  label,
  description,
  checked,
  onCheckedChange,
  icon,
}: {
  label: string;
  description: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  icon: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between p-4 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-smooth">
      <div className="flex items-start space-x-3 flex-1">
        <div className={`p-2 rounded-lg ${checked ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"} transition-colors`}>
          {icon}
        </div>
        <div className="flex-1">
          <Label className="text-sm font-semibold cursor-pointer">{label}</Label>
          <p className="text-xs text-muted-foreground font-mono mt-1">{description}</p>
        </div>
      </div>
      <Switch checked={checked} onCheckedChange={onCheckedChange} />
    </div>
  );
}
