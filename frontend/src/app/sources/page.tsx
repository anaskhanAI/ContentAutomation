"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { api } from "@/lib/api";
import type { Source } from "@/lib/types";

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [filteredSources, setFilteredSources] = useState<Source[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newSource, setNewSource] = useState({ name: "", url: "", source_type: "ai_research" });

  const fetchSources = async () => {
    try {
      const data = await api.getSources();
      setSources(data);
      setFilteredSources(data);
    } catch (error) {
      console.error("Failed to fetch sources:", error);
    }
  };

  useEffect(() => {
    fetchSources();
  }, []);

  useEffect(() => {
    // Ensure sources is an array before filtering
    if (!Array.isArray(sources)) {
      setFilteredSources([]);
      return;
    }
    
    let filtered = sources;
    
    if (searchQuery) {
      filtered = filtered.filter(s => 
        s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.url.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    if (filterType !== "all") {
      filtered = filtered.filter(s => s.source_type === filterType);
    }
    
    setFilteredSources(filtered);
  }, [searchQuery, filterType, sources]);

  const handleToggle = async (id: string, currentState: boolean) => {
    try {
      await api.toggleSource(id, !currentState);
      fetchSources();
    } catch (error) {
      console.error("Failed to toggle source:", error);
    }
  };

  const handleArticleCountChange = async (id: string, count: number) => {
    try {
      await api.updateSource(id, { max_articles: count });
      fetchSources();
    } catch (error) {
      console.error("Failed to update article count:", error);
    }
  };

  const handlePriorityChange = async (id: string, priority: string) => {
    try {
      await api.updateSource(id, { priority });
      fetchSources();
    } catch (error) {
      console.error("Failed to update priority:", error);
    }
  };

  const handleAddSource = async () => {
    try {
      await api.addSource(newSource);
      setIsAddDialogOpen(false);
      setNewSource({ name: "", url: "", source_type: "ai_research" });
      fetchSources();
    } catch (error) {
      console.error("Failed to add source:", error);
    }
  };

  const handleDeleteSource = async (id: string) => {
    if (!confirm("Are you sure you want to delete this source?")) return;
    try {
      await api.deleteSource(id);
      fetchSources();
    } catch (error) {
      console.error("Failed to delete source:", error);
    }
  };

  // Ensure sources is always an array
  const sourcesArray = Array.isArray(sources) ? sources : [];
  const filteredArray = Array.isArray(filteredSources) ? filteredSources : [];
  
  const sourceTypes = [...new Set(sourcesArray.map(s => s.source_type))];
  const groupedSources = filteredArray.reduce((acc, source) => {
    if (!acc[source.source_type]) acc[source.source_type] = [];
    acc[source.source_type].push(source);
    return acc;
  }, {} as Record<string, Source[]>);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight gradient-text">Content Sources</h1>
          <p className="text-muted-foreground font-mono mt-2">Manage your content scraping sources</p>
        </div>
        
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button size="lg" className="glass bg-primary/10 hover:bg-primary/20 border-primary/20 text-primary font-semibold group">
              <svg className="w-5 h-5 mr-2 group-hover:rotate-90 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Source
            </Button>
          </DialogTrigger>
          <DialogContent className="glass border-border/40">
            <DialogHeader>
              <DialogTitle className="text-2xl gradient-text">Add New Source</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <Label htmlFor="name" className="font-mono">Source Name</Label>
                <Input
                  id="name"
                  value={newSource.name}
                  onChange={(e) => setNewSource({ ...newSource, name: e.target.value })}
                  placeholder="OpenAI Blog"
                  className="mt-2 glass border-border/40 font-mono"
                />
              </div>
              <div>
                <Label htmlFor="url" className="font-mono">URL</Label>
                <Input
                  id="url"
                  value={newSource.url}
                  onChange={(e) => setNewSource({ ...newSource, url: e.target.value })}
                  placeholder="https://openai.com/blog"
                  className="mt-2 glass border-border/40 font-mono"
                />
              </div>
              <div>
                <Label htmlFor="type" className="font-mono">Source Type</Label>
                <Select value={newSource.source_type} onValueChange={(v) => setNewSource({ ...newSource, source_type: v })}>
                  <SelectTrigger className="mt-2 glass border-border/40 font-mono">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="glass border-border/40">
                    <SelectItem value="ai_research">AI Research</SelectItem>
                    <SelectItem value="ai_news">AI News</SelectItem>
                    <SelectItem value="tech_blog">Tech Blog</SelectItem>
                    <SelectItem value="company_blog">Company Blog</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button onClick={handleAddSource} className="w-full bg-primary hover:bg-primary/90 font-semibold">
                Add Source
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search and Filter */}
      <div className="flex items-center space-x-4">
        <div className="flex-1 relative">
          <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <Input
            placeholder="Search sources..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 glass border-border/40 font-mono"
          />
        </div>
        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-48 glass border-border/40 font-mono">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="glass border-border/40">
            <SelectItem value="all">All Types</SelectItem>
            {sourceTypes.map(type => (
              <SelectItem key={type} value={type}>{type.replace(/_/g, " ").toUpperCase()}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-4">
        <StatMini label="Total Sources" value={sourcesArray.length} color="from-primary to-emerald-500" />
        <StatMini label="Active" value={sourcesArray.filter(s => s.is_active).length} color="from-blue-500 to-cyan-500" />
        <StatMini label="Inactive" value={sourcesArray.filter(s => !s.is_active).length} color="from-yellow-500 to-orange-500" />
        <StatMini label="Types" value={sourceTypes.length} color="from-purple-500 to-pink-500" />
      </div>

      {/* Sources Grid */}
      <div className="space-y-6">
        {Object.entries(groupedSources).map(([type, typeSources]) => (
          <div key={type}>
            <h2 className="text-xl font-semibold mb-4 font-mono flex items-center">
              <div className="w-1 h-6 bg-gradient-to-b from-primary to-blue-500 rounded-full mr-3"></div>
              {type.replace(/_/g, " ").toUpperCase()}
              <span className="ml-3 text-sm text-muted-foreground">({typeSources.length})</span>
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {typeSources.map((source) => (
                <SourceCard
                  key={source.id}
                  source={source}
                  onToggle={handleToggle}
                  onArticleCountChange={handleArticleCountChange}
                  onPriorityChange={handlePriorityChange}
                  onDelete={handleDeleteSource}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SourceCard({
  source,
  onToggle,
  onArticleCountChange,
  onPriorityChange,
  onDelete,
}: {
  source: Source;
  onToggle: (id: string, currentState: boolean) => void;
  onArticleCountChange: (id: string, count: number) => void;
  onPriorityChange: (id: string, priority: string) => void;
  onDelete: (id: string) => void;
}) {
  const hasRSS = source.metadata?.has_rss;
  const maxArticles = source.metadata?.max_articles || 3;
  const priority = source.metadata?.priority || "normal";

  return (
    <Card className={`glass border-border/40 p-6 card-hover transition-smooth ${source.is_active ? "" : "opacity-60"}`}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-lg flex items-center">
              {source.name}
              {hasRSS && (
                <span className="ml-2 px-2 py-0.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-mono">
                  RSS
                </span>
              )}
            </h3>
            <p className="text-sm text-muted-foreground font-mono mt-1 truncate">{source.url}</p>
          </div>
          <Switch checked={source.is_active} onCheckedChange={() => onToggle(source.id, source.is_active)} />
        </div>

        {/* Stats */}
        <div className="flex items-center space-x-4 text-xs font-mono">
          <div className="flex items-center space-x-1">
            <svg className="w-4 h-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-muted-foreground">
              {source.last_scraped_at ? new Date(source.last_scraped_at).toLocaleDateString() : "Never"}
            </span>
          </div>
        </div>

        {/* Controls */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label className="text-xs font-mono text-muted-foreground">Articles</Label>
            <Select value={maxArticles.toString()} onValueChange={(v) => onArticleCountChange(source.id, parseInt(v))}>
              <SelectTrigger className="mt-1 glass border-border/40 font-mono h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="glass border-border/40">
                {[1, 2, 3, 5, 10].map(n => (
                  <SelectItem key={n} value={n.toString()}>{n} articles</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label className="text-xs font-mono text-muted-foreground">Priority</Label>
            <Select value={priority} onValueChange={(v) => onPriorityChange(source.id, v)}>
              <SelectTrigger className="mt-1 glass border-border/40 font-mono h-9">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="glass border-border/40">
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="normal">Normal</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-2 border-t border-border/40">
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-mono text-primary hover:underline flex items-center"
          >
            Visit Source
            <svg className="w-3 h-3 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
          <Button
            onClick={() => onDelete(source.id)}
            variant="ghost"
            size="sm"
            className="text-destructive hover:bg-destructive/10 h-7 text-xs font-mono"
          >
            Delete
          </Button>
        </div>
      </div>
    </Card>
  );
}

function StatMini({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <Card className="glass border-border/40 p-4">
      <p className="text-xs text-muted-foreground font-mono mb-1">{label}</p>
      <p className="text-2xl font-bold font-mono gradient-text">{value}</p>
    </Card>
  );
}
