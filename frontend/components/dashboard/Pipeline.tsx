"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Circle, Loader2, FileSearch } from "lucide-react";
import { cn } from "@/lib/utils";
import { useVideo, VideoStatus } from "./VideoContext";
import { ScriptReview } from "./ScriptReview";

// Pipeline step definitions
const STEPS = [
  {
    id: 1,
    title: "Material Processing (RAG)",
    description: "Retrieving context from knowledge base",
    activeStatuses: ["planning"] as VideoStatus[],
    completedStatuses: ["scripting", "waiting_approval", "generating", "rendering", "stitching", "completed"] as VideoStatus[],
  },
  {
    id: 2,
    title: "Script Generation (LLM)",
    description: "Writing narration & scene breakdown",
    activeStatuses: ["scripting"] as VideoStatus[],
    completedStatuses: ["waiting_approval", "generating", "rendering", "stitching", "completed"] as VideoStatus[],
    showReviewButton: true,
  },
  {
    id: 3,
    title: "Code Generation (Manim)",
    description: "Generating Python code for animations",
    activeStatuses: ["generating"] as VideoStatus[],
    completedStatuses: ["rendering", "stitching", "completed"] as VideoStatus[],
  },
  {
    id: 4,
    title: "Video Rendering (FFmpeg)",
    description: "Compiling final video output",
    activeStatuses: ["rendering", "stitching"] as VideoStatus[],
    completedStatuses: ["completed"] as VideoStatus[],
  },
];

function getStepStatus(
  step: typeof STEPS[0],
  currentStatus: VideoStatus
): "completed" | "processing" | "pending" {
  if (step.completedStatuses.includes(currentStatus)) {
    return "completed";
  }
  if (step.activeStatuses.includes(currentStatus)) {
    return "processing";
  }
  return "pending";
}

export function Pipeline() {
  const { currentVideoId, videoStatus, isPolling } = useVideo();
  const [showReview, setShowReview] = useState(false);

  const isActive = currentVideoId && videoStatus !== "idle";
  const isWaitingApproval = videoStatus === "waiting_approval";

  return (
    <div className="space-y-4 h-full flex flex-col">
      <Card className="w-full border shadow-sm bg-white flex-1">
        <CardHeader className="pb-3 border-b bg-gray-50/50">
          <CardTitle className="text-base font-semibold flex justify-between items-center">
            <span className="flex items-center gap-2">
              Generation Pipeline
              {isPolling && (
                <span className="flex items-center gap-1 text-[10px] font-normal text-muted-foreground">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                  Live
                </span>
              )}
            </span>
            {currentVideoId && (
              <span className="text-xs font-normal text-muted-foreground font-mono">
                {currentVideoId.slice(0, 8)}...
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-8 p-6">
          {STEPS.map((step, index) => {
            const status = isActive
              ? getStepStatus(step, videoStatus)
              : "pending";
            const isScriptStep = step.id === 2;

            return (
              <div key={step.id} className="flex items-start gap-4 relative">
                {/* Line connector */}
                {index !== STEPS.length - 1 && (
                  <div
                    className={cn(
                      "absolute left-[11px] top-7 h-full w-[2px]",
                      status === "completed" ? "bg-green-200" : "bg-gray-100"
                    )}
                  />
                )}

                <div className="relative z-10 flex h-6 w-6 items-center justify-center bg-white ring-4 ring-white">
                  {status === "completed" && (
                    <CheckCircle2 className="h-6 w-6 text-green-500" />
                  )}
                  {status === "processing" && (
                    <Loader2 className="h-6 w-6 text-indigo-600 animate-spin" />
                  )}
                  {status === "pending" && (
                    <Circle className="h-6 w-6 text-gray-200" />
                  )}
                </div>
                <div className="grid gap-1 -mt-1 flex-1">
                  <div className="flex items-center justify-between">
                    <p
                      className={cn(
                        "text-sm font-medium leading-none",
                        status === "pending" ? "text-gray-400" : "text-gray-900"
                      )}
                    >
                      {step.title}
                    </p>
                    {/* Show review button on script step when waiting approval */}
                    {isScriptStep && isWaitingApproval && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-6 text-[10px] gap-1 bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100"
                        onClick={() => setShowReview(true)}
                      >
                        <FileSearch className="w-3 h-3" />
                        Review Scripts
                      </Button>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {step.description}
                  </p>
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Script Review Modal/Panel */}
      {showReview && isWaitingApproval && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-2xl">
            <ScriptReview onClose={() => setShowReview(false)} />
            <Button
              variant="ghost"
              size="sm"
              className="mt-2 w-full text-white hover:bg-white/10"
              onClick={() => setShowReview(false)}
            >
              Close
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
