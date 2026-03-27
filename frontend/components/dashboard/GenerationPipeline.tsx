"use client";

import { useEffect, useRef, useState } from "react";
import { CheckCircle2, Loader2, Circle, Play, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useVideo, VideoStatus } from "./VideoContext";
import { ScriptReview } from "./ScriptReview";
import { VideoPlayer } from "./VideoPlayer";

// =============================================================================
// Step definitions mapped to backend statuses
// =============================================================================

const STEPS = [
  {
    id: 1,
    emoji: "🧠",
    label: "Understanding your topic...",
    activeStatuses: ["planning"] as VideoStatus[],
    completedStatuses: [
      "scripting", "waiting_approval", "generating",
      "rendering", "stitching", "completed",
    ] as VideoStatus[],
  },
  {
    id: 2,
    emoji: "📚",
    label: "Aligning with curriculum...",
    activeStatuses: ["scripting"] as VideoStatus[],
    completedStatuses: [
      "waiting_approval", "generating",
      "rendering", "stitching", "completed",
    ] as VideoStatus[],
  },
  {
    id: 3,
    emoji: "✍️",
    label: "Writing script...",
    activeStatuses: ["waiting_approval"] as VideoStatus[],
    completedStatuses: [
      "generating", "rendering", "stitching", "completed",
    ] as VideoStatus[],
    isHITL: true,
  },
  {
    id: 4,
    emoji: "🎬",
    label: "Creating animations...",
    activeStatuses: ["generating"] as VideoStatus[],
    completedStatuses: ["rendering", "stitching", "completed"] as VideoStatus[],
  },
  {
    id: 5,
    emoji: "🔊",
    label: "Adding voiceover...",
    activeStatuses: ["rendering"] as VideoStatus[],
    completedStatuses: ["stitching", "completed"] as VideoStatus[],
  },
  {
    id: 6,
    emoji: "📦",
    label: "Rendering final video...",
    activeStatuses: ["stitching"] as VideoStatus[],
    completedStatuses: ["completed"] as VideoStatus[],
  },
];

function getStepState(
  step: (typeof STEPS)[0],
  currentStatus: VideoStatus
): "completed" | "active" | "pending" {
  if (step.completedStatuses.includes(currentStatus)) return "completed";
  if (step.activeStatuses.includes(currentStatus)) return "active";
  return "pending";
}

// =============================================================================
// Component
// =============================================================================

export function GenerationPipeline() {
  const { currentVideoId, videoStatus, videoData, isPolling } = useVideo();
  const [showPlayer, setShowPlayer] = useState(false);
  const activeRef = useRef<HTMLDivElement>(null);

  const isActive = currentVideoId && videoStatus !== "idle";
  const isCompleted = videoStatus === "completed";
  const isFailed = videoStatus === "failed";
  const videoUrl = videoData?.final_video_url;

  // Auto-scroll to the active step
  useEffect(() => {
    if (activeRef.current) {
      activeRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [videoStatus]);

  if (!isActive) return null;

  return (
    <div className="w-full max-w-3xl mx-auto mt-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
        {/* Header */}
        <div className="px-5 py-3 border-b bg-gray-50/60 flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700 flex items-center gap-2">
            Generation Progress
            {isPolling && (
              <span className="flex items-center gap-1 text-[10px] font-normal text-muted-foreground">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                Live
              </span>
            )}
          </span>
          {currentVideoId && (
            <span className="text-[10px] font-mono text-muted-foreground">
              {currentVideoId.slice(0, 8)}...
            </span>
          )}
        </div>

        {/* Steps */}
        <div className="px-5 py-5 space-y-0">
          {STEPS.map((step, index) => {
            const state = getStepState(step, videoStatus);
            const isLast = index === STEPS.length - 1;

            return (
              <div key={step.id}>
                <div
                  ref={state === "active" ? activeRef : undefined}
                  className={cn(
                    "flex items-start gap-3 relative transition-all duration-500",
                    state === "pending" && "opacity-40",
                    state === "active" && "opacity-100",
                    state === "completed" && "opacity-100"
                  )}
                  style={{
                    transitionDelay: `${index * 80}ms`,
                  }}
                >
                  {/* Vertical connector */}
                  {!isLast && (
                    <div
                      className={cn(
                        "absolute left-[15px] top-8 w-[2px] h-[calc(100%)]",
                        state === "completed"
                          ? "bg-green-200"
                          : state === "active"
                          ? "bg-[#F875AA]/30"
                          : "bg-gray-100"
                      )}
                    />
                  )}

                  {/* Icon */}
                  <div className="relative z-10 flex h-8 w-8 items-center justify-center flex-shrink-0 bg-white rounded-full ring-4 ring-white">
                    {state === "completed" && (
                      <CheckCircle2 className="h-6 w-6 text-green-500" />
                    )}
                    {state === "active" && (
                      <Loader2 className="h-5 w-5 text-[#F875AA] animate-spin" />
                    )}
                    {state === "pending" && (
                      <Circle className="h-5 w-5 text-gray-200" />
                    )}
                  </div>

                  {/* Label */}
                  <div className="pt-1 pb-6 flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-base">{step.emoji}</span>
                      <p
                        className={cn(
                          "text-sm font-medium",
                          state === "active"
                            ? "text-[#e8609a]"
                            : state === "completed"
                            ? "text-gray-700"
                            : "text-gray-400"
                        )}
                      >
                        {step.label}
                      </p>
                    </div>

                    {/* HITL: Inline script review when waiting_approval or completed */}
                    {step.isHITL && (state === "active" || state === "completed") && (
                      <div className="mt-3 animate-in fade-in slide-in-from-top-2 duration-300">
                        <ScriptReview />
                      </div>
                    )}

                    {/* Final step: Watch Video button */}
                    {isLast && isCompleted && (
                      <div className="mt-2">
                        <Button
                          size="sm"
                          className="h-7 text-xs gap-1.5 bg-green-600 hover:bg-green-700 text-white"
                          onClick={() => setShowPlayer(true)}
                        >
                          <Play className="w-3 h-3" />
                          Watch Video
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Failed state */}
        {isFailed && (
          <div className="px-5 pb-4">
            <div className="text-xs p-2.5 rounded-lg bg-red-50 text-red-700 border border-red-100 flex items-center gap-2">
              <X className="w-3 h-3 flex-shrink-0" />
              Generation failed. Please try again.
            </div>
          </div>
        )}
      </div>

      {/* Video Player Modal */}
      {showPlayer && isCompleted && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-4xl">
            <div className="bg-gray-900 rounded-lg overflow-hidden">
              <div className="flex justify-between items-center p-3 border-b border-gray-800">
                <h3 className="text-white font-medium text-sm">Generated Video</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 text-gray-400 hover:text-white hover:bg-gray-800"
                  onClick={() => setShowPlayer(false)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <div className="aspect-video">
                <VideoPlayer videoUrl={videoUrl} />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
