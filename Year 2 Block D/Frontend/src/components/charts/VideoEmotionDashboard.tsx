// src/components/charts/VideoEmotionDashboard.tsx

import React, { useState, useEffect, useRef } from "react";
import ReactPlayer from "react-player";
import Papa from "papaparse";
import {
  LineChart,
  Line,
  Scatter,
  ComposedChart,
  ReferenceArea,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";

interface DashboardProps {
  videoUrl: string;
  csvUrl: string;
}

interface RawRow {
  start: string;       // "hh:mm:ss,ms"
  emotion: string;
  intensity_score?: number;
  confidence?: number;
}

const EMOTION_COLORS: Record<string, string> = {
  neutral:        "#696969",
  desire:         "#6F6F6F",
  realization:    "#767676",
  caring:         "#7D7D7D",
  admiration:     "#848484",

  optimism:       "#E6C200",
  pride:          "#CCAC00",
  curiosity:      "#B39300",
  amusement:      "#998000",
  joy:            "#7F6C00",
  gratitude:      "#665800",
  approval:       "#4C4400",
  relief:         "#332F00",
  love:           "#1A1A00",

  disappointment: "#1C86EE",
  sadness:        "#1874CD",
  remorse:        "#1565BD",
  embarrassment:  "#124EAD",

  fear:           "#4B0082",
  nervousness:    "#520D8A",

  annoyance:      "#DC143C",
  anger:          "#C1122D",

  excitement:     "#FF8C00",
  confusion:      "#E07B00",
  surprise:       "#C06900",

  disapproval:    "#228B22",
  disgust:        "#1E7A1E",
};

export default function VideoEmotionDashboard({ videoUrl, csvUrl }: DashboardProps) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const playerRef = useRef<ReactPlayer>(null);

  // parse "hh:mm:ss,ms" → seconds
  const parseTime = (hmsMs: string) => {
    const [hms, msStr] = hmsMs.split(",");
    const [hh, mm, ss] = (hms || "0:0:0").split(":").map(Number);
    const ms = Number(msStr || "0");
    return hh * 3600 + mm * 60 + ss + ms / 1000;
  };

  useEffect(() => {
    setLoading(true);

    Papa.parse<RawRow>(csvUrl, {
      download: true,
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: ({ data: rows }) => {
        if (!rows.length) {
          setData([]);
          setLoading(false);
          return;
        }

        const hasScore = rows[0].hasOwnProperty("intensity_score");

        if (hasScore) {
          // ————— Intensity‑mode chart data —————
          const chart = rows.map(r => ({
            time:            parseTime(r.start),
            intensity_score: r.intensity_score ?? 0,
            emotion:         r.emotion,
            confidence:      r.confidence ?? 0,
          }));
          chart.sort((a, b) => a.time - b.time);
          setData(chart);

        } else {
          // ————— Stripe‑mode segments —————
          const pts = rows.map(r => ({
            time:    parseTime(r.start),
            emotion: r.emotion,
          }));
          pts.sort((a, b) => a.time - b.time);

          // build [start, end] per row using next start as end
          const segments = pts.map((p, i) => ({
            startSec: p.time,
            endSec:   i < pts.length - 1 ? pts[i + 1].time : p.time + 0.5,
            emotion:  p.emotion,
          }));
          setData(segments);
        }

        setLoading(false);
      },
      error: () => setLoading(false),
    });
  }, [csvUrl]);

  // track playback time
  useEffect(() => {
    const iv = setInterval(() => {
      const t = playerRef.current?.getCurrentTime() || 0;
      setCurrentTime(t);
    }, 200);
    return () => clearInterval(iv);
  }, []);

  if (loading) {
    return <p className="text-center py-4">Loading chart…</p>;
  }

  const hasScore = data.length > 0 && data[0].hasOwnProperty("intensity_score");

  return (
    <div className="space-y-6">
      <ReactPlayer
        ref={playerRef}
        url={videoUrl}
        controls
        width="100%"
        height="360px"
      />

      <ResponsiveContainer width="100%" height={hasScore ? 300 : 80}>
        {hasScore ? (
          // ————— Original LineChart + Scatter —————
          <LineChart
            data={data}
            onClick={(e) => {
              if (e?.activePayload && playerRef.current) {
                playerRef.current.seekTo(e.activePayload[0].payload.time, "seconds");
              }
            }}
            margin={{ top: 10, right: 30, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis
              dataKey="time"
              type="number"
              domain={[0, "dataMax"]}
              tickFormatter={s => `${s.toFixed(0)}s`}
              label={{ value: "Time (s)", position: "insideBottomRight", offset: -10 }}
            />
            <YAxis
              dataKey="intensity_score"
              type="number"
              domain={[0, "dataMax"]}
              label={{ value: "Intensity Score", angle: -90, position: "insideLeft" }}
            />
            <Tooltip
              formatter={(val, name) => {
                if (name === "time") return [`${(val as number).toFixed(1)}s`, "Time"];
                return [val, name.charAt(0).toUpperCase() + name.slice(1)];
              }}
              labelFormatter={lbl => `Time: ${lbl.toFixed(1)}s`}
            />
            <Legend />
            <ReferenceLine x={currentTime} stroke="red" strokeDasharray="3 3" />

            <Line type="monotone" dataKey="intensity_score" stroke="#8884d8" dot={false} />

            {Object.entries(EMOTION_COLORS).map(([emo, color]) => (
              <Scatter
                key={emo}
                data={data.filter(d => d.emotion === emo)}
                dataKey="time"
                fill={color}
                name={emo}
              />
            ))}
          </LineChart>
        ) : (
          // ————— Stripe ComposedChart —————
          <ComposedChart
            data={data}
            onClick={(e) => {
              const start = e?.activePayload?.[0]?.payload?.startSec;
              if (start != null && playerRef.current) {
                playerRef.current.seekTo(start, "seconds");
              }
            }}
            margin={{ top: 0, right: 0, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" opacity={0.1} vertical={false} />
            <XAxis
              dataKey="startSec"
              type="number"
              domain={[0, "dataMax"]}
              tickFormatter={s => `${s.toFixed(0)}s`}
              axisLine={false}
              tickLine={false}
              height={20}
            />
            <YAxis domain={[0, 1]} hide />
            <Tooltip
              cursor={{ fill: "rgba(0,0,0,0.1)" }}
              formatter={(_, __, entry) => [entry.payload.emotion, "Emotion"]}
              labelFormatter={() => ""}
            />

            {data.map((seg, i) => (
              <ReferenceArea
                key={i}
                x1={seg.startSec}
                x2={seg.endSec}
                y1={0}
                y2={1}
                fill={EMOTION_COLORS[seg.emotion] || "#ccc"}
              />
            ))}

            <ReferenceLine x={currentTime} stroke="red" strokeDasharray="3 3" />
          </ComposedChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}


