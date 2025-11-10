// pages/History.tsx
import React, { useState, useEffect } from "react";
import {
  Download as DownloadIcon,
  BarChart2,
  XCircle,
  Calendar,
  Clock,
  BarChart3,
  MessageSquare,
  CheckCircle2,
  Smile,
  Loader2,
  ArrowRight,
  CheckCircle,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Papa from "papaparse";

const API_BASE = import.meta.env.VITE_API_BASE_URL!;

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import Navigation from "@/components/layout/Navigation";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogTitle, DialogClose } from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

import VideoEmotionDashboard from "@/components/charts/VideoEmotionDashboard";
import EmotionChart from "@/components/charts/EmotionChart";
import EmotionPieChart from "@/components/charts/EmotionPieChart";
import EmotionTranscript from "@/components/charts/EmotionTranscript";

interface HistoryItem {
  id: string;
  timestamp: string;
  url: string;
  plan: string;
  downloadLink: string;
  feedbackSubmitted?: boolean;
}

interface TranscriptSegment {
  id: number;
  start: string;
  end: string;
  sentence: string;
  translation: string;
  emotion: string;
}

const EMOTION_OPTIONS = [
  "neutral",
  "happy",
  "sad",
  "angry",
  "surprised",
  "fearful",
  "disgusted",
] as const;

type FeedbackState =
  | "idle"
  | "loading"
  | "prompting"
  | "editing"
  | "confirming"
  | "submitting"
  | "submitted";

export default function PredictionHistory() {
  const [historyData, setHistoryData] = useState<HistoryItem[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [modalItem, setModalItem] = useState<HistoryItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [feedbackItem, setFeedbackItem] = useState<HistoryItem | null>(null);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);

  const [transcriptSegments, setTranscriptSegments] = useState<TranscriptSegment[]>([]);
  const [originalSegments, setOriginalSegments] = useState<TranscriptSegment[]>([]);
  const [feedbackState, setFeedbackState] = useState<FeedbackState>("idle");
  const [madeCorrections, setMadeCorrections] = useState(false);

  const itemsPerPage = 5;
  const totalPages = Math.ceil(historyData.length / itemsPerPage);
  const pageSlice = historyData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  useEffect(() => {
    const saved = localStorage.getItem("emotionAnalysisHistory");
    if (saved) {
      try {
        setHistoryData(JSON.parse(saved));
      } catch {
        setHistoryData([]);
      }
    }
  }, []);

  const persistHistory = (newHistory: HistoryItem[]) => {
    localStorage.setItem("emotionAnalysisHistory", JSON.stringify(newHistory));
    setHistoryData(newHistory);
  };

  const markFeedbackAsSubmitted = (link: string) => {
    const newHist = historyData.map((h) =>
      h.downloadLink === link ? { ...h, feedbackSubmitted: true } : h
    );
    persistHistory(newHist);
  };

  const exportAll = () => {
    if (!historyData.length) return;
    const rows = historyData.map((i) =>
      [new Date(i.timestamp).toLocaleString(), i.url, i.plan, i.downloadLink].join(",")
    );
    const csv = ["Timestamp,URL,Plan,DownloadLink", ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = Object.assign(document.createElement("a"), {
      href: url,
      download: `history-${new Date().toISOString().slice(0, 10)}.csv`,
    });
    a.click();
    URL.revokeObjectURL(url);
  };

  const clearAll = () => {
    if (window.confirm("Clear history?")) persistHistory([]);
  };

  const deleteItem = (id: string) => {
    if (window.confirm("Delete this entry?"))
      persistHistory(historyData.filter((h) => h.id !== id));
  };

  const openFeedback = async (item: HistoryItem) => {
    if (item.feedbackSubmitted) {
      alert("Feedback already submitted ✅");
      return;
    }
    setFeedbackItem(item);
    setIsFeedbackOpen(true);
    setFeedbackState("loading");
    try {
      const res = await fetch(item.downloadLink);
      if (!res.ok) throw new Error(res.statusText);
      const txt = await res.text();
      const parsed = Papa.parse(txt, { header: true, skipEmptyLines: true });
      const segs = (parsed.data as any[]).map((row, idx) => ({
        ...row,
        id: idx,
        emotion: row.emotion?.trim() || "neutral",
      }));
      setTranscriptSegments(segs);
      setOriginalSegments(segs);
      setFeedbackState("prompting");
    } catch (e) {
      console.error(e);
      setIsFeedbackOpen(false);
      setFeedbackState("idle");
    }
  };

  const handleEmotionChange = (id: number, emotion: string) =>
    setTranscriptSegments((cur) =>
      cur.map((s) => (s.id === id ? { ...s, emotion } : s))
    );

  const handleCorrectSubmit = async () => {
    if (!feedbackItem) return;
    setFeedbackState("submitting");
    const fn = feedbackItem.downloadLink.split("/").pop()!;
    try {
      await fetch(`${API_BASE}/api/predictions/${encodeURIComponent(fn)}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ correct: true }),
      });
      setFeedbackState("submitted");
      markFeedbackAsSubmitted(feedbackItem.downloadLink);
    } catch (e) {
      console.error(e);
      setFeedbackState("prompting");
    }
  };

  const handleFinalSubmit = async () => {
    if (!feedbackItem) return;
    setFeedbackState("submitting");
    setMadeCorrections(true);
    const fn = feedbackItem.downloadLink.split("/").pop()!;
    try {
      await fetch(`${API_BASE}/api/predictions/${encodeURIComponent(fn)}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ correct: false, corrections: transcriptSegments }),
      });
      setFeedbackState("submitted");
      markFeedbackAsSubmitted(feedbackItem.downloadLink);
    } catch (e) {
      console.error(e);
      setFeedbackState("editing");
    }
  };

  const downloadCorrectedData = () => {
    const orig = feedbackItem!.downloadLink.split("/").pop()!;
    const csv = Papa.unparse(transcriptSegments, {
      columns: ["start", "end", "sentence", "translation", "emotion"],
    });
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = Object.assign(document.createElement("a"), {
      href: url,
      download: `corrected-${orig}`,
    });
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderFeedbackContent = () => {
    switch (feedbackState) {
      case "loading":
        return (
          <motion.div key="loading" className="flex justify-center py-8">
            <Loader2 className="animate-spin text-primary h-8 w-8" />
          </motion.div>
        );
      case "prompting":
        return (
          <motion.div key="prompting" className="space-y-4 text-center">
            <h3 className="text-lg font-semibold">
              Is the initial analysis correct?
            </h3>
            <div className="flex justify-center gap-4">
              <Button onClick={handleCorrectSubmit}>
                <CheckCircle2 className="mr-2 h-4 w-4" />
                Yes, looks good
              </Button>
              <Button variant="outline" onClick={() => setFeedbackState("editing")}>
                <XCircle className="mr-2 h-4 w-4" />
                Nope, let me fix it
              </Button>
            </div>
          </motion.div>
        );
      case "editing": {
        const changes = transcriptSegments.filter(
          (s, i) => s.emotion !== originalSegments[i]?.emotion
        ).length;
        return (
          <motion.div key="editing" className="space-y-4">
            <div className="max-h-[50vh] overflow-y-auto border p-2 bg-muted/20 space-y-2">
              {transcriptSegments.map((seg) => (
                <div
                  key={seg.id}
                  className="grid grid-cols-12 gap-2 p-2 hover:bg-background rounded"
                >
                  <div className="col-span-8">
                    <p className="text-xs text-muted-foreground">
                      {seg.start} – {seg.end}
                    </p>
                    <p>“{seg.sentence}”</p>
                  </div>
                  <div className="col-span-4">
                    <Select
                      value={seg.emotion}
                      onValueChange={(e) => handleEmotionChange(seg.id, e)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select emotion" />
                      </SelectTrigger>
                      <SelectContent>
                        {EMOTION_OPTIONS.map((opt) => (
                          <SelectItem key={opt} value={opt}>
                            {opt}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex justify-end">
              <Button
                onClick={() => setFeedbackState("confirming")}
                disabled={changes === 0}
              >
                Review {changes} Change{changes !== 1 && "s"}
              </Button>
            </div>
          </motion.div>
        );
      }
      case "confirming": {
        const changed = transcriptSegments.filter(
          (s, i) => s.emotion !== originalSegments[i]?.emotion
        );
        return (
          <motion.div key="confirming" className="space-y-4">
            <h3 className="text-lg font-semibold text-center">
              Review Your Changes
            </h3>
            <div className="max-h-[50vh] overflow-y-auto border p-3 bg-muted/20 space-y-2">
              {changed.map((seg, i) => (
                <React.Fragment key={seg.id}>
                  <div>
                    <p className="italic">“{seg.sentence}”</p>
                    <div className="flex items-center justify-end text-xs text-muted-foreground">
                      <Badge variant="destructive">
                        {originalSegments.find((s) => s.id === seg.id)?.emotion}
                      </Badge>
                      <ArrowRight className="h-3 w-3 mx-1" />
                      <Badge variant="secondary">{seg.emotion}</Badge>
                    </div>
                  </div>
                  {i < changed.length - 1 && <Separator />}
                </React.Fragment>
              ))}
            </div>
            <div className="flex justify-between">
              <Button variant="ghost" onClick={() => setFeedbackState("editing")}>
                Go Back
              </Button>
              <Button onClick={handleFinalSubmit}>Confirm & Submit</Button>
            </div>
          </motion.div>
        );
      }
      case "submitting":
        return (
          <motion.div key="submitting" className="flex flex-col items-center py-8">
            <Loader2 className="animate-spin text-primary h-8 w-8" />
            <p className="mt-2 text-sm text-muted-foreground">
              Submitting feedback…
            </p>
          </motion.div>
        );
      case "submitted":
        return (
          <motion.div key="submitted" className="text-center space-y-4">
            <Smile size={48} className="mx-auto text-green-500" />
            <p className="font-semibold text-lg">Thank you! 🎉</p>
            <div className="flex justify-center gap-4">
              {madeCorrections && (
                <Button variant="outline" onClick={downloadCorrectedData}>
                  Download Corrections
                </Button>
              )}
              <DialogClose asChild>
                <Button>Close</Button>
              </DialogClose>
            </div>
          </motion.div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />
      <main className="flex-1 p-8">
        {/* Header buttons */}
        <div className="flex gap-3 mb-6">
          <Button onClick={exportAll} disabled={!historyData.length}>
            <DownloadIcon className="mr-2 h-5 w-5" />
            Export All
          </Button>
          <Button onClick={clearAll} variant="outline" disabled={!historyData.length}>
            Clear History
          </Button>
        </div>

        {/* History Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 />
              Analysis History
            </CardTitle>
          </CardHeader>
          <CardContent>
            {historyData.length ? (
              <>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Video URL</TableHead>
                      <TableHead>Plan</TableHead>
                      <TableHead className="text-center">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pageSlice.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>
                          <div className="flex flex-col">
                            <span className="flex items-center gap-1">
                              <Calendar className="h-4 w-4 text-muted-foreground" />
                              {new Date(item.timestamp).toLocaleDateString()}
                            </span>
                            <span className="flex items-center gap-1 text-xs text-muted-foreground">
                              <Clock className="h-3 w-3" />
                              {new Date(item.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="underline text-primary"
                          >
                            {item.url}
                          </a>
                        </TableCell>
                        <TableCell>
                          <Badge className="capitalize">
                            {item.plan === "basic"
                              ? "Starter"
                              : item.plan === "plus"
                              ? "Creator"
                              : "Enterprise"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-center">
                          <div className="flex items-center justify-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => window.open(item.downloadLink, "_blank")}
                            >
                              <DownloadIcon className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setModalItem(item);
                                setIsModalOpen(true);
                              }}
                            >
                              <BarChart2 className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => deleteItem(item.id)}
                            >
                              <XCircle className="h-4 w-4 text-red-500" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => openFeedback(item)}
                              disabled={item.feedbackSubmitted}
                            >
                              {item.feedbackSubmitted ? (
                                <CheckCircle className="h-4 w-4 text-green-500" />
                              ) : (
                                <MessageSquare className="h-4 w-4 text-blue-500" />
                              )}
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                {totalPages > 1 && (
                  <div className="mt-4 flex justify-center">
                    <Pagination>
                      <PaginationContent>
                        <PaginationItem>
                          <PaginationPrevious onClick={() => setCurrentPage((p) => Math.max(1, p - 1))} />
                        </PaginationItem>
                        {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                          <PaginationItem key={p}>
                            <PaginationLink isActive={p === currentPage} onClick={() => setCurrentPage(p)}>
                              {p}
                            </PaginationLink>
                          </PaginationItem>
                        ))}
                        <PaginationItem>
                          <PaginationNext onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))} />
                        </PaginationItem>
                      </PaginationContent>
                    </Pagination>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <p>No analysis history yet.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </main>

      {/* Analysis Views Dialog */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-3xl p-4">
          <DialogTitle className="sr-only">Analysis Views</DialogTitle>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Analysis Views</h2>
            <DialogClose asChild>
              <Button variant="ghost">✕ Close</Button>
            </DialogClose>
          </div>
          {modalItem && (
            <Tabs defaultValue="dashboard" className="space-y-4">
              <TabsList className="mb-2 space-x-2">
                <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
                <TabsTrigger value="timeline">Timeline</TabsTrigger>
                <TabsTrigger value="distribution">Distribution</TabsTrigger>
                <TabsTrigger value="transcript">Transcript</TabsTrigger>
              </TabsList>
              <TabsContent value="dashboard">
                <VideoEmotionDashboard
                  videoUrl={modalItem.url}
                  csvUrl={modalItem.downloadLink}
                />
              </TabsContent>
              <TabsContent value="timeline">
                <EmotionChart csvUrl={modalItem.downloadLink} isLoading={false} />
              </TabsContent>
              <TabsContent value="distribution">
                <EmotionPieChart csvUrl={modalItem.downloadLink} isLoading={false} />
              </TabsContent>
              <TabsContent value="transcript">
                <EmotionTranscript csvUrl={modalItem.downloadLink} />
              </TabsContent>
            </Tabs>
          )}
        </DialogContent>
      </Dialog>

      {/* Feedback Dialog */}
      <Dialog open={isFeedbackOpen} onOpenChange={setIsFeedbackOpen}>
        <DialogContent className="max-w-2xl p-4">
          <DialogTitle className="sr-only">Give Feedback</DialogTitle>
          <Card className="overflow-visible border-0 shadow-none">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Smile className="text-yellow-500" /> Give Feedback
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <AnimatePresence mode="wait">
                {renderFeedbackContent()}
              </AnimatePresence>
            </CardContent>
          </Card>
        </DialogContent>
      </Dialog>
    </div>
  );
}

