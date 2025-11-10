import React, { useRef, useState } from "react";
import {
  ArrowRight,
  Upload,
  Sparkles,
  Video,
  BarChart3,
  CheckCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import Navigation from "@/components/layout/Navigation";
import SubscriptionPlans from "@/components/SubscriptionPlans";
import { Badge } from "@/components/ui/badge";
import { useUpload } from "@/context/UploadContext";
import GrainOverlay from "@/components/GrainOverlay";
import { useToast } from "@/hooks/use-toast";

const Index = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const { setFile } = useUpload();
  const { toast } = useToast();

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setFile(file);
    toast({
      title: "File Uploaded",
      description: `${file.name} selected successfully!`,
      icon: <CheckCircle className="h-5 w-5 text-green-400" />,
    });

    setTimeout(() => {
      navigate("/analysis");
      setUploading(false);
    }, 1200);
  };

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground relative overflow-hidden">
      <GrainOverlay />

      {/* Background blobs */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-0 right-[10%] w-96 h-96 rounded-full bg-gradient-to-br from-primary/20 via-accent/15 to-transparent filter blur-[120px] animate-pulse-light" />
        <div className="absolute bottom-0 left-[5%] w-80 h-80 rounded-full bg-gradient-to-tr from-accent/20 via-primary/15 to-transparent filter blur-[100px] animate-float" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 h-72 rounded-full bg-gradient-to-r from-primary/10 to-accent/10 filter blur-[80px] animate-glow" />
        <div className="absolute top-1/4 right-[20%] w-64 h-64 rounded-full bg-gradient-to-l from-green-500/15 to-blue-500/10 filter blur-[90px] animate-float" style={{ animationDelay: "3s" }} />
        <div className="absolute bottom-1/3 left-[15%] w-56 h-56 rounded-full bg-gradient-to-r from-purple-500/15 to-pink-500/10 filter blur-[100px] animate-pulse-light" style={{ animationDelay: "1.5s" }} />
        <div className="absolute top-2/3 right-[8%] w-48 h-48 rounded-full bg-gradient-to-br from-yellow-500/10 to-orange-500/15 filter blur-[80px] animate-glow" style={{ animationDelay: "4s" }} />
      </div>

      <div className="noise-overlay opacity-40" />
      <Navigation />

      <main className="flex-1 relative z-10">
        {/* Hero */}
        <section className="py-20 md:py-32">
          <div className="container mx-auto px-4 md:px-6 text-center space-y-10">
            <Badge className="inline-flex items-center bg-gradient-to-r from-primary/20 to-accent/20 text-primary border-primary/30 backdrop-blur-sm px-6 py-2 text-sm font-medium animate-fade-in">
              <Sparkles className="w-4 h-4 mr-2" />
              AI-Powered Emotion Intelligence
            </Badge>

            <h1 className="text-4xl md:text-7xl font-bold tracking-tight animate-slide-up">
              <span className="text-foreground">Welcome back!</span><br />
              <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent bg-[length:200%_auto] animate-shimmer">
                Ready to understand emotions deeper than ever?
              </span>
            </h1>

            <p className="text-muted-foreground text-lg md:text-xl leading-relaxed animate-slide-up">
              Upload content or access recent results. Your insights, your control.
            </p>

            <div className="flex flex-wrap justify-center gap-4 animate-slide-up">
              <Button
                size="lg"
                onClick={handleUploadClick}
                disabled={uploading}
                className="bg-gradient-to-r from-primary to-accent text-white shadow-2xl group px-8 py-4 text-lg flex items-center"
              >
                <Upload className="mr-2 h-5 w-5" />
                {uploading ? "Processing…" : "Select File"}
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>

              <input
                ref={fileInputRef}
                type="file"
                accept=".mp3,.mp4,.txt,.csv"
                className="hidden"
                onChange={handleFileChange}
              />

              <Button
                size="lg"
                variant="outline"
                onClick={() => navigate("/analysis")}
                className="glass-card border-primary/30 px-8 py-4 text-lg flex items-center"
              >
                <Video className="mr-2 h-5 w-5" /> Try Sample Video
              </Button>

              <Button
                size="lg"
                variant="outline"
                onClick={() => navigate("/history")}
                className="glass-card border-accent/30 px-8 py-4 text-lg flex items-center"
              >
                <BarChart3 className="mr-2 h-5 w-5" /> Explore Dashboard
              </Button>
            </div>

            <p className="text-muted-foreground text-sm italic mt-8">
              Empowered by privacy-safe AI. Built to analyze, learn, and evolve.
            </p>
          </div>
        </section>

        {/* Subscription Plans */}
        <section className="py-20 md:py-32 border-t border-white/10">
          <div className="container mx-auto px-4 md:px-6 text-center">
            <h2 className="text-3xl md:text-5xl font-bold mb-6 text-gradient">
              Choose Your Plan
            </h2>
            <p className="text-muted-foreground text-xl max-w-3xl mx-auto mb-8">
              From personal projects to enterprise solutions, we have the perfect plan for your emotional AI needs
            </p>
            <SubscriptionPlans />
          </div>
        </section>

        {/* Flourish Chart */}
        <section className="py-20 md:py-32 bg-background border-t border-white/10">
          <div className="container mx-auto px-4 md:px-6 text-center">
            <h2 className="text-3xl md:text-5xl font-bold mb-4 text-gradient">
              Core and extra emotions
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto mb-6">
              See the differences of the emotion distribution of the models.
            </p>
            <div className="aspect-w-16 aspect-h-9">
              <iframe
                src="https://public.flourish.studio/visualisation/23782274/embed"
                title="Flourish Chart"
                frameBorder="0"
                allowFullScreen
                className="w-full h-[600px] rounded-xl shadow-xl"
              />
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Index;

