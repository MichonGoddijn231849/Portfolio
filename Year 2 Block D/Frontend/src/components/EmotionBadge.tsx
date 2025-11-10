
import React from "react";
import { Badge } from "@/components/ui/badge";

interface EmotionBadgeProps {
  emotion: string;
  intensity: number;
}

const EmotionBadge: React.FC<EmotionBadgeProps> = ({ emotion, intensity }) => {
  const getColor = () => {
    switch (emotion) {
      case "joy":
        return "bg-emotion-joy/20 text-emotion-joy border-emotion-joy/40 shadow-emotion-joy/25";
      case "sadness":
        return "bg-emotion-sadness/20 text-emotion-sadness border-emotion-sadness/40 shadow-emotion-sadness/25";
      case "anger":
        return "bg-emotion-anger/20 text-emotion-anger border-emotion-anger/40 shadow-emotion-anger/25";
      case "fear":
        return "bg-emotion-fear/20 text-emotion-fear border-emotion-fear/40 shadow-emotion-fear/25";
      case "surprise":
        return "bg-emotion-surprise/20 text-emotion-surprise border-emotion-surprise/40 shadow-emotion-surprise/25";
      case "neutral":
        return "bg-emotion-neutral/20 text-emotion-neutral border-emotion-neutral/40 shadow-emotion-neutral/25";
      case "complex":
        return "bg-emotion-complex/20 text-emotion-complex border-emotion-complex/40 shadow-emotion-complex/25";
      default:
        return "bg-secondary/30 text-muted-foreground border-border/50";
    }
  };

  return (
    <Badge 
      variant="outline"
      className={`flex items-center gap-2 ${getColor()} py-2 px-4 rounded-lg border backdrop-blur-sm shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-xl`}
    >
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${emotion === 'joy' ? 'bg-emotion-joy' : 
          emotion === 'sadness' ? 'bg-emotion-sadness' :
          emotion === 'anger' ? 'bg-emotion-anger' :
          emotion === 'fear' ? 'bg-emotion-fear' :
          emotion === 'surprise' ? 'bg-emotion-surprise' :
          emotion === 'neutral' ? 'bg-emotion-neutral' :
          emotion === 'complex' ? 'bg-emotion-complex' : 'bg-muted'
        } animate-pulse`} />
        <span className="font-semibold capitalize">{emotion}</span>
      </div>
      {intensity > 0 && (
        <>
          <div className="h-4 w-0.5 bg-border/50 mx-1" />
          <span className="text-xs font-mono font-bold">{intensity}%</span>
        </>
      )}
    </Badge>
  );
};

export default EmotionBadge;
