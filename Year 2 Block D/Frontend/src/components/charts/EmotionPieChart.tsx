import React from "react";
import Papa from "papaparse";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LegendPayload,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface EmotionPieChartProps {
  csvUrl: string;
  isLoading?: boolean;
}

// Map each emotion to its primary, slightly darker color
const EMOTION_COLOR_MAP: Record<string, string> = {
  // Neutral family (grey tones)
  neutral:     "#696969",
  desire:      "#6F6F6F",
  realization: "#767676",
  caring:      "#7D7D7D",
  admiration:  "#848484",

  // Happy family (warm yellows)
  optimism:  "#E6C200",
  pride:     "#CCAC00",
  curiosity: "#B39300",
  amusement: "#998000",
  joy:       "#7F6C00",
  gratitude: "#665800",
  approval:  "#4C4400",
  relief:    "#332F00",
  love:      "#1A1A00",

  // Sad family (deep blues)
  disappointment: "#1C86EE",
  sadness:       "#1874CD",
  remorse:       "#1565BD",
  embarrassment: "#124EAD",

  // Scared family (dark purples)
  fear:        "#4B0082",
  nervousness: "#520D8A",

  // Mad family (crimson reds)
  annoyance: "#DC143C",
  anger:     "#C1122D",

  // Surprised family (burnt oranges)
  excitement: "#FF8C00",
  confusion:  "#E07B00",
  surprise:   "#C06900",

  // Disgusted family (forest greens)
  disapproval: "#228B22",
  disgust:     "#1E7A1E",
};

const EmotionPieChart: React.FC<EmotionPieChartProps> = ({ csvUrl, isLoading = false }) => {
  const [data, setData] = React.useState<{ name: string; value: number }[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [hiddenEmotions, setHiddenEmotions] = React.useState<Set<string>>(new Set());

  React.useEffect(() => {
    if (!csvUrl) {
      setData([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    Papa.parse(csvUrl, {
      download: true,
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results) => {
        const rawRows = results.data as Array<Record<string, any>>;
        const counts: Record<string, number> = {};

        rawRows.forEach((row) => {
          const emo = row["emotion"] || row["Emotion"] || "";
          const name = String(emo).trim().toLowerCase();
          if (!name) return;
          counts[name] = (counts[name] || 0) + 1;
        });

        const familyOrder: Record<string, number> = {
          neutral: 0, desire: 0, realization: 0, caring: 0, admiration: 0,
          optimism: 1, pride: 1, curiosity: 1, amusement: 1, joy: 1, gratitude: 1, approval: 1, relief: 1, love: 1,
          disappointment: 2, sadness: 2, remorse: 2, embarrassment: 2,
          fear: 3, nervousness: 3,
          annoyance: 4, anger: 4,
          excitement: 5, confusion: 5, surprise: 5,
          disapproval: 6, disgust: 6,
        };

        const pieData = Object.entries(counts)
          .map(([name, value]) => ({ name, value }))
          .sort((a, b) => {
            const famA = familyOrder[a.name] ?? 99;
            const famB = familyOrder[b.name] ?? 99;
            return famA !== famB ? famA - famB : b.value - a.value;
          });

        setData(pieData);
        setLoading(false);
      },
      error: (err) => {
        console.error("Error parsing CSV for pie chart:", err);
        setData([]);
        setLoading(false);
      },
    });
  }, [csvUrl]);

  const handleLegendClick = (entry: LegendPayload) => {
    const name = String(entry.value).toLowerCase();
    setHiddenEmotions(prev => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  const displayedData = data.filter(d => !hiddenEmotions.has(d.name));

  if (loading || isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Emotion Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center py-8 text-muted-foreground">Loading…</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center justify-between">
          Emotion Distribution
        </CardTitle>
      </CardHeader>
      <CardContent>
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={displayedData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }) => `${name} ${(percent! * 100).toFixed(0)}%`}
              >
                {displayedData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={EMOTION_COLOR_MAP[entry.name] || "#CCCCCC"}
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value: any, name: any) => [`${value}`, name]} />
              <Legend
                layout="horizontal"
                verticalAlign="bottom"
                height={36}
                payload={data.map(d => ({ value: d.name, type: 'square', color: EMOTION_COLOR_MAP[d.name] }))}
                onClick={handleLegendClick}
                formatter={(value) => (
                  <span style={{ opacity: hiddenEmotions.has(String(value).toLowerCase()) ? 0.5 : 1 }}>
                    {value}
                  </span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-center py-8 text-muted-foreground">
            No emotion data to display.
          </p>
        )}
      </CardContent>
    </Card>
  );
};

export default EmotionPieChart;
