import React from "react";
import Papa from "papaparse";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface TranscriptRow {
  start: string;
  end: string;
  sentence: string;
  emotion: string;
}

interface EmotionTranscriptProps {
  csvUrl: string;
}

// Semi-transparent variants of the darker palette
const EMOTION_COLORS: Record<string, string> = {
  // Neutral family
  neutral:     "#69696933",
  desire:      "#6F6F6F33",
  realization: "#76767633",
  caring:      "#7D7D7333",
  admiration:  "#84848433",

  // Happy family
  optimism:  "#E6C20033",
  pride:     "#CCAC0033",
  curiosity: "#B3930033",
  amusement: "#99800033",
  joy:       "#7F6C0033",
  gratitude: "#66580033",
  approval:  "#4C440033",
  relief:    "#332F0033",
  love:      "#1A1A0033",

  // Sad family
  disappointment: "#1C86EE33",
  sadness:       "#1874CD33",
  remorse:       "#1565BD33",
  embarrassment: "#124EAD33",

  // Scared family
  fear:        "#4B008233",
  nervousness: "#520D8A33",

  // Mad family
  annoyance: "#DC143C33",
  anger:     "#C1122D33",

  // Surprised family
  excitement: "#FF8C0033",
  confusion:  "#E07B0033",
  surprise:   "#C0690033",

  // Disgusted family
  disapproval: "#228B2233",
  disgust:     "#1E7A1E33",
};

export default function EmotionTranscript({ csvUrl }: EmotionTranscriptProps) {
  const [rows, setRows] = React.useState<TranscriptRow[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    setLoading(true);
    Papa.parse(csvUrl, {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: ({ data }) => {
        const parsed = (data as any[])
          .map(r => ({
            start: r.start || r.Start,
            end: r.end || r.End,
            sentence: r.sentence || r.Sentence,
            emotion: (r.emotion || r.Emotion).toLowerCase(),
          }))
          .filter(r => r.sentence && r.emotion);
        setRows(parsed);
        setLoading(false);
      },
      error: () => setLoading(false),
    });
  }, [csvUrl]);

  if (loading) return <p>Loading transcript…</p>;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Transcript</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 max-h-80 overflow-y-auto">
        {rows.map((row, i) => (
          <div
            key={i}
            style={{ backgroundColor: EMOTION_COLORS[row.emotion] || "transparent" }}
            className="p-2 rounded"
          >
            <div className="text-xs text-muted-foreground">
              {row.start} – {row.end}{' '}
              <span className="capitalize">({row.emotion})</span>
            </div>
            <div>{row.sentence}</div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
