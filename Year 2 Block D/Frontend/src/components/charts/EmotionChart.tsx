// src/components/charts/EmotionChart.tsx

import React from "react";
import Papa from "papaparse";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface EmotionChartProps {
  csvUrl: string;
  isLoading?: boolean;
}

const EmotionChart: React.FC<EmotionChartProps> = ({ csvUrl, isLoading = false }) => {
  const [data, setData] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);

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
        // Debug: log the first few rows so you can inspect them in the console
        console.log("EmotionChart parsed rows:", results.data.slice(0, 5));

        const rawRows = results.data as Array<Record<string, any>>;

        // 1) Group by the "start" timestamp (string format "HH:mm:ss,SSS")
        const timelineMap: Record<string, Record<string, number>> = {};
        rawRows.forEach((row) => {
          // CSV column name: either "start" (lowercase) or maybe "Start"
          const ts = row["start"] || row["Start"] || "";
          const emo = row["emotion"] || row["Emotion"] || "";
          if (!ts || !emo) return;

          const e = String(emo).trim();
          if (!timelineMap[ts]) {
            timelineMap[ts] = {
              joy: 0,
              sadness: 0,
              anger: 0,
              fear: 0,
              surprise: 0,
              neutral: 0,
            };
          }
          // Increment count for that emotion at this timestamp
          timelineMap[ts][e] = (timelineMap[ts][e] || 0) + 1;
        });

        // 2) Convert timestamp strings into a sortable number (milliseconds)
        const toMs = (t: string) => {
          // t looks like "00:00:30,000" (meaning 30 seconds exactly)
          const [hms, msStr] = String(t).split(",");
          const [hh, mm, ss] = hms.split(":").map(Number);
          const ms = Number(msStr);
          return hh * 3600000 + mm * 60000 + ss * 1000 + ms;
        };

        // 3) Build a sorted array, with an incrementing timePoint (in seconds)
        const sortedTimestamps = Object.keys(timelineMap).sort((a, b) => toMs(a) - toMs(b));
        const timelineArray = sortedTimestamps.map((ts, idx) => ({
          // You can also compute actual seconds via toMs(ts) / 1000
          timePoint: (toMs(ts) / 1000).toFixed(0), // string of seconds
          ...timelineMap[ts],
        }));

        setData(timelineArray);
        setLoading(false);
      },
      error: (err) => {
        console.error("Error parsing CSV for line chart:", err);
        setData([]);
        setLoading(false);
      },
    });
  }, [csvUrl]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center justify-between">
          Emotion Timeline
          {(isLoading || loading) && (
            <span className="text-xs font-normal text-muted-foreground animate-pulse">
              Loading…
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-center py-8 text-muted-foreground">Loading data…</p>
        ) : data.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis
                dataKey="timePoint"
                label={{ value: "Time (s)", position: "insideBottomRight", offset: -10 }}
              />
              <YAxis label={{ value: "Count", angle: -90, position: "insideLeft" }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="joy" stroke="#FFD166" strokeWidth={2} />
              <Line type="monotone" dataKey="sadness" stroke="#118AB2" strokeWidth={2} />
              <Line type="monotone" dataKey="anger" stroke="#EF476F" strokeWidth={2} />
              <Line type="monotone" dataKey="fear" stroke="#073B4C" strokeWidth={2} />
              <Line type="monotone" dataKey="surprise" stroke="#06D6A0" strokeWidth={2} />
              <Line type="monotone" dataKey="neutral" stroke="#8A817C" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-center py-8 text-muted-foreground">No timeline data to display.</p>
        )}
      </CardContent>
    </Card>
  );
};

export default EmotionChart;
