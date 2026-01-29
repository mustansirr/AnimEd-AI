"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import { getVideoStatus, getScenes, VideoStatusResponse, SceneResponse } from "@/lib/api";

// =============================================================================
// Types
// =============================================================================

export type VideoStatus =
  | "idle"
  | "planning"
  | "scripting"
  | "waiting_approval"
  | "generating"
  | "rendering"
  | "stitching"
  | "completed"
  | "failed";

interface VideoContextType {
  currentVideoId: string | null;
  videoStatus: VideoStatus;
  videoData: VideoStatusResponse | null;
  scenes: SceneResponse[];
  isPolling: boolean;
  error: string | null;
  setCurrentVideoId: (id: string | null) => void;
  refreshStatus: () => Promise<void>;
  refreshScenes: () => Promise<void>;
}

// =============================================================================
// Context
// =============================================================================

const VideoContext = createContext<VideoContextType | undefined>(undefined);

export function useVideo() {
  const context = useContext(VideoContext);
  if (context === undefined) {
    throw new Error("useVideo must be used within a VideoProvider");
  }
  return context;
}

// =============================================================================
// Provider
// =============================================================================

interface VideoProviderProps {
  children: ReactNode;
}

export function VideoProvider({ children }: VideoProviderProps) {
  const [currentVideoId, setCurrentVideoId] = useState<string | null>(null);
  const [videoStatus, setVideoStatus] = useState<VideoStatus>("idle");
  const [videoData, setVideoData] = useState<VideoStatusResponse | null>(null);
  const [scenes, setScenes] = useState<SceneResponse[]>([]);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshStatus = useCallback(async () => {
    if (!currentVideoId) return;

    try {
      const data = await getVideoStatus(currentVideoId);
      setVideoData(data);
      setVideoStatus(data.status as VideoStatus);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get status");
    }
  }, [currentVideoId]);

  const refreshScenes = useCallback(async () => {
    if (!currentVideoId) return;

    try {
      const scenesData = await getScenes(currentVideoId);
      setScenes(scenesData);
      setError(null);
    } catch (err) {
      // Scenes might not exist yet, that's okay
      console.log("No scenes yet:", err);
    }
  }, [currentVideoId]);

  // Poll for status updates while video is processing
  useEffect(() => {
    if (!currentVideoId) {
      setIsPolling(false);
      return;
    }

    // Status values that indicate processing is complete
    const terminalStatuses: VideoStatus[] = ["completed", "failed", "idle"];
    
    if (terminalStatuses.includes(videoStatus)) {
      setIsPolling(false);
      return;
    }

    // Special case: waiting_approval - poll less frequently
    const pollInterval = videoStatus === "waiting_approval" ? 5000 : 2000;

    setIsPolling(true);
    const interval = setInterval(() => {
      refreshStatus();
      // Also refresh scenes when we hit waiting_approval
      if (videoStatus === "scripting" || videoStatus === "waiting_approval") {
        refreshScenes();
      }
    }, pollInterval);

    // Initial fetch
    refreshStatus();

    return () => {
      clearInterval(interval);
      setIsPolling(false);
    };
  }, [currentVideoId, videoStatus, refreshStatus, refreshScenes]);

  // Reset state when video ID changes
  useEffect(() => {
    if (currentVideoId) {
      setVideoStatus("planning");
      setScenes([]);
      setError(null);
    } else {
      setVideoStatus("idle");
      setVideoData(null);
      setScenes([]);
    }
  }, [currentVideoId]);

  return (
    <VideoContext.Provider
      value={{
        currentVideoId,
        videoStatus,
        videoData,
        scenes,
        isPolling,
        error,
        setCurrentVideoId,
        refreshStatus,
        refreshScenes,
      }}
    >
      {children}
    </VideoContext.Provider>
  );
}
