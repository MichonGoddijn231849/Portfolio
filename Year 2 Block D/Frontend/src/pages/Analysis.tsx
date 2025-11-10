import React, { useState, useEffect } from "react";
import {
  Download,
  Wand2,
  BarChart2,
  Loader2,
  Sparkles,
  CheckCircle,
  X as XIcon // Renamed to avoid conflict
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Navigation from "@/components/layout/Navigation";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { useToast } from "@/hooks/use-toast";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import PlanFeatureComparison from "@/components/PlanFeatureComparison";
import EmotionTierDisplay from "@/components/EmotionTierDisplay";
import { useUpload } from "@/context/UploadContext";
import { useNavigate } from "react-router-dom";

const API = import.meta.env.VITE_API_BASE_URL || "http://194.171.191.226:3100";

const planOptions = [
  { id: "basic", label: "Starter", price: "Free", model: "tiny" },
  { id: "plus", label: "Creator", price: "$12/mo", model: "medium", popular: true },
  { id: "pro", label: "Enterprise", price: "$49/mo", model: "turbo" },
];

const Analysis = () => {
  const { toast } = useToast();
  // 1. Get the NEW clearFile function from our updated context
  const { file, clearFile } = useUpload();
  const navigate = useNavigate();

  const [url, setUrl] = useState("");
  const [plan, setPlan] = useState(planOptions[0].id);
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [tab, setTab] = useState("input");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [downloadLink, setDownloadLink] = useState<string | null>(null);
  
  useEffect(() => {
    if (file) {
      setUrl('');
    }
  }, [file]);

  useEffect(() => {
    if (!loading) return;
    const id = setInterval(() => {
      setProgress((p) => Math.min(90, p + Math.random() * 15));
    }, 800);
    return () => clearInterval(id);
  }, [loading]);

  // 2. THE FIX: This function now correctly clears the file from context
  const handleReset = () => {
    clearFile(); // This is the crucial line that was missing
    setUrl("");
    setStartTime("");
    setEndTime("");
    setPlan(planOptions[0].id);
    setDownloadLink(null);
    setProgress(0);
    setLoading(false);
    setTab("input");
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file && !url) {
      toast({ variant: "destructive", title: "No Input Found", description: "Please upload a file or provide a URL." });
      return;
    }
    setLoading(true);
    setDownloadLink(null);
    setProgress(10);
    try {
      const formData = new FormData();
      if (file) {
        formData.append("file", file);
      } else {
        formData.append("src", url);
      }
      if (startTime) formData.append("start_time", startTime);
      if (endTime) formData.append("end_time", endTime);
      formData.append("translate", "false");
      formData.append("classify", "false");
      formData.append("classify_ext", "false");
      formData.append("intensity", "false");

      const res = await fetch(`${API}/predict-any`, {
        method: "POST",
        headers: { "x-plan": plan },
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(
          Array.isArray(err.detail)
            ? err.detail.map((d) => d.msg).join(", ")
            : err.detail || `Error ${res.status}`
        );
      }
      
      setProgress(100);
      const data = await res.json();
      const link = data.download?.link;
      if (!link) throw new Error("Download link missing");
      setDownloadLink(link);

      const historyItem = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        url: file ? file.name : url,
        plan,
        downloadLink: link,
      };
      const existing = JSON.parse(localStorage.getItem("emotionAnalysisHistory") || "[]");
      localStorage.setItem("emotionAnalysisHistory", JSON.stringify([historyItem, ...existing].slice(0, 50)));

      setTab("results");
      toast({ title: "Analysis Complete", description: "CSV ready for download." });
    } catch (err: any) {
      setLoading(false);
      setProgress(0);
      toast({ variant: "destructive", title: "Error", description: err.message });
    }
  };

  const download = () => downloadLink && window.open(downloadLink, "_blank");
  
  const handleTrySample = () => {
    handleReset();
    setUrl("https://www.youtube.com/watch?v=... (Sample)");
    setTab("input");
  }

  // 3. This array now correctly points to the fully working handleReset function
  const nextActions = [
    {
      title: "View In History",
      icon: <BarChart2 className="h-5 w-5" />,
      action: () => navigate("/history"),
    },
    {
      title: "Analyze Another",
      icon: <Wand2 className="h-5 w-5" />,
      action: handleReset,
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground overflow-hidden">
      <Navigation />
      <main className="flex-1 p-4 md:p-8">
        <header className="text-center mb-8">
          <Badge className="bg-gradient-to-r from-primary/20 to-accent/20 text-primary inline-flex items-center px-4 py-2 mb-4">
            <Sparkles className="mr-2 h-4 w-4" /> AI-Powered Hybrid Analysis
          </Badge>
          <h1 className="text-4xl font-bold mb-2">Emotion Analysis Studio</h1>
          <p className="text-muted-foreground">
            Upload a file or enter a URL for analysis.
          </p>
        </header>

        <Tabs value={tab} onValueChange={setTab} className="max-w-2xl mx-auto">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="input">1. Input & Configure</TabsTrigger>
            <TabsTrigger value="results" disabled={!downloadLink}>2. Results</TabsTrigger>
          </TabsList>
          <TabsContent value="input" className="mt-6">
            <Card className="p-6 md:p-8">
              <form onSubmit={submit} className="space-y-6">
                {file ? (
                  <div className="p-4 border-dashed border-primary bg-primary/10 rounded-lg flex items-center justify-between">
                    <div className="flex items-center gap-3 font-medium text-primary overflow-hidden">
                      <CheckCircle className="h-5 w-5 flex-shrink-0"/>
                      <span className="truncate" title={file.name}>{file.name}</span>
                    </div>
                    {/* The X button also correctly clears the file now */}
                    <Button variant="ghost" size="icon" onClick={clearFile}><XIcon className="h-4 w-4"/></Button>
                  </div>
                ) : (
                  <div>
                    <Label htmlFor="url">YouTube URL or Media Link</Label>
                    <Input id="url" value={url} onChange={(e) => setUrl(e.target.value)} disabled={loading || !!file} placeholder="https://youtube.com/watch?v=..."/>
                  </div>
                )}
                <div className="text-center">
                  <Button type="button" variant="link" onClick={handleTrySample}>Or try a sample video</Button>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="start-time">Start Time (HH:MM:SS)</Label>
                    <Input id="start-time" value={startTime} onChange={(e) => setStartTime(e.target.value)} disabled={loading} placeholder="e.g., 00:01:30"/>
                  </div>
                  <div>
                    <Label htmlFor="end-time">End Time (HH:MM:SS)</Label>
                    <Input id="end-time" value={endTime} onChange={(e) => setEndTime(e.target.value)} disabled={loading} placeholder="Optional"/>
                  </div>
                </div>
                <div>
                  <Label>Analysis Model</Label>
                  <RadioGroup value={plan} onValueChange={setPlan} className="grid grid-cols-3 gap-4 mt-2">
                    {planOptions.map(({ id, label }) => (
                      <Card key={id} className={`p-4 flex items-center justify-center cursor-pointer ${plan === id ? 'border-primary ring-2 ring-primary' : ''}`}>
                        <RadioGroupItem value={id} id={id} className="sr-only" />
                        <Label htmlFor={id} className="font-medium cursor-pointer">{label}</Label>
                      </Card>
                    ))}
                  </RadioGroup>
                </div>
                <Button type="submit" disabled={loading || (!file && !url)} className="w-full h-12 text-lg">
                  {loading ? (<><Loader2 className="animate-spin mr-2" /> Analyzing…</>) : (<><Wand2 className="mr-2" /> Analyze</>)}
                </Button>
                {loading && <Progress value={progress} className="h-2 mt-4" />}
              </form>
              <div className="mt-8">
                <PlanFeatureComparison selectedPlan={plan} />
              </div>
            </Card>
          </TabsContent>
          <TabsContent value="results" className="mt-6">
            <Card className="p-6 md:p-8 space-y-6 text-center">
              <CheckCircle className="mx-auto h-16 w-16 text-green-500" />
              <div className="space-y-1">
                <h2 className="text-3xl font-bold">Analysis Complete!</h2>
                <p className="text-muted-foreground">Your file has been processed successfully.</p>
              </div>
              <Button onClick={download} size="lg" className="w-full"><Download className="mr-2" />Download Results (.csv)</Button>
              <EmotionTierDisplay plan={plan} />
              <div className="grid md:grid-cols-2 gap-4 pt-4">
                {nextActions.map(({ title, icon, action }) => (
                  <Button key={title} variant="outline" onClick={action} className="flex items-center gap-2">{icon}<span>{title}</span></Button>
                ))}
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Analysis;
