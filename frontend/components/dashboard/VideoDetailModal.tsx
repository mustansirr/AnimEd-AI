"use client";

import { useEffect } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useVideo, VideoStatus } from "./VideoContext";
import { GenerationPipeline } from "./GenerationPipeline";

interface VideoDetailModalProps {
  videoId: string;
  videoStatus: string;
  videoPrompt: string;
  onClose: () => void;
}

export function VideoDetailModal({
  videoId,
  videoStatus: initialStatus,
  videoPrompt,
  onClose,
}: VideoDetailModalProps) {
  const { setCurrentVideoId } = useVideo();

  // Set the video ID on mount so VideoContext loads its status and scenes
  useEffect(() => {
    setCurrentVideoId(videoId, initialStatus as VideoStatus);

    return () => {
      // Clear when modal closes
      setCurrentVideoId(null);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [videoId]);

  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 flex items-start justify-center overflow-y-auto p-4 pt-12"
      onClick={onClose}
    >
      <div
        className="w-full max-w-2xl mb-12"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex-1 min-w-0 mr-4">
            <h2 className="text-lg font-semibold text-white truncate">
              {videoPrompt}
            </h2>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-gray-400 hover:text-white hover:bg-white/10 flex-shrink-0"
            onClick={onClose}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Pipeline (renders itself based on VideoContext state) */}
        <GenerationPipeline />
      </div>
    </div>
  );
}
