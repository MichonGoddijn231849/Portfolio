
import React from "react";
import { Info } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface EmotionTierDisplayProps {
  plan: string;
}

const emotionsByPlan = {
  basic: [
    "happy", "sad", "mad", "scared", "surprised", "disgusted", "neutral"
  ],
  plus: [
    "excitement", "confusion", "surprise", "neutral", "optimism", "pride",
    "curiosity", "fear", "amusement", "joy", "desire", "annoyance",
    "nervousness", "gratitude", "approval", "realization", "disappointment",
    "caring", "sadness", "admiration", "disapproval", "anger", "remorse"
  ],
  pro: [
    "excitement", "confusion", "surprise", "neutral", "optimism", "pride",
    "curiosity", "fear", "amusement", "joy", "desire", "annoyance",
    "nervousness", "gratitude", "approval", "realization", "disappointment",
    "caring", "sadness", "admiration", "disapproval", "anger", "remorse",
    "relief", "love", "disgust", "embarrassment"
  ]
};

const EmotionTierDisplay: React.FC<EmotionTierDisplayProps> = ({ plan }) => {
  const emotions = emotionsByPlan[plan as keyof typeof emotionsByPlan] || emotionsByPlan.basic;
  const displayCount = 12;
  const displayedEmotions = emotions.slice(0, displayCount);
  const hiddenCount = emotions.length - displayCount;

  const getBgGradient = () => {
    if (plan === "basic") return "bg-background";
    if (plan === "plus") return "bg-background";
    return "bg-background";
  };

  return (
    <Card className={`border-border ${getBgGradient()} glass-card rounded-xl`}>
      <CardContent className="p-5 space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-sm font-medium text-foreground">
            Available Emotions
          </h3>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="rounded-full bg-secondary/60 p-1.5 hover:bg-secondary transition-colors cursor-help">
                  <Info className="h-3.5 w-3.5 text-muted-foreground" />
                </div>
              </TooltipTrigger>
              <TooltipContent className="bg-secondary/90 backdrop-blur-md border-border">
                <p className="text-xs">
                  {plan === "basic" ? "Basic emotions only" : 
                  plan === "plus" ? "25+ advanced emotions" : 
                  "Complete set of 30+ emotions"}
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {displayedEmotions.map((emotion) => (
            <Badge 
              key={emotion} 
              variant="outline"
              className="bg-secondary/50 border-border hover:bg-secondary transition-all duration-200 text-xs capitalize"
            >
              {emotion}
            </Badge>
          ))}
          
          {hiddenCount > 0 && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Badge 
                    variant="outline"
                    className="bg-primary/10 hover:bg-primary/20 text-primary border-primary/30 cursor-help transition-all duration-200"
                  >
                    +{hiddenCount} more
                  </Badge>
                </TooltipTrigger>
                <TooltipContent className="bg-secondary/90 backdrop-blur-md border-border max-w-xs">
                  <div>
                    <p className="text-xs mb-2">Additional emotions in this tier:</p>
                    <div className="flex flex-wrap gap-1.5">
                      {emotions.slice(displayCount).map((emotion) => (
                        <Badge key={emotion} variant="outline" className="text-[10px] capitalize bg-secondary/50 border-border">
                          {emotion}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>

        <div className="text-xs text-muted-foreground">
          <p className="mb-2">
            {plan === "basic" ? "Basic tier includes 7 fundamental emotions." : 
            plan === "plus" ? "Creator tier provides 25+ advanced emotion categories." : 
            "Enterprise tier offers the full suite of 30+ emotions with cultural context."}
          </p>
          
          <div className="flex items-center gap-1.5 mt-2">
            <span className="font-mono bg-secondary/50 text-muted-foreground rounded px-2 py-0.5 text-[10px]">
              {plan === "basic" ? "tiny" : plan === "plus" ? "medium" : "turbo"}
            </span> 
            <span>transcription model</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default EmotionTierDisplay;
