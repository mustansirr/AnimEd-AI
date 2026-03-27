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
  setCurrentVideoId: (id: string | null, initialStatus?: VideoStatus) => void;
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
  const [error, setError] = useState<string | null>(null);
  // Status values that indicate processing is paused or complete (no polling needed)
  const terminalStatuses: VideoStatus[] = ["completed", "failed", "idle", "waiting_approval"];
  
  // Derived state
  const isPolling = !!currentVideoId && !terminalStatuses.includes(videoStatus);

  const handleSetCurrentVideoId = (id: string | null, initialStatus?: VideoStatus) => {
    setCurrentVideoId(id);
    if (id) {
      setVideoStatus(initialStatus || "planning");
      setScenes([]);
      setError(null);
    } else {
      setVideoStatus("idle");
      setVideoData(null);
      setScenes([]);
    }
  };

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
    if (!isPolling) return;

    const pollInterval = 2000;

    const interval = setInterval(() => {
      refreshStatus();
      // Also refresh scenes when scripting is in progress
      if (videoStatus === "scripting") {
        refreshScenes();
      }
    }, pollInterval);

    // Initial fetch
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refreshStatus();

    return () => {
      clearInterval(interval);
    };
  }, [isPolling, videoStatus, refreshStatus, refreshScenes]);

  // Fetch scenes when status transitions to waiting_approval or when opening a completed/later stage video
  // This is separate from polling since we stop polling during waiting_approval
  useEffect(() => {
    const statusesWithScripts = ["waiting_approval", "generating", "rendering", "stitching", "completed"];
    if (currentVideoId && statusesWithScripts.includes(videoStatus)) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      refreshScenes();
    }
  }, [videoStatus, currentVideoId, refreshScenes]);

  return (
    <VideoContext.Provider
      value={{
        currentVideoId,
        videoStatus,
        videoData,
        scenes,
        isPolling,
        error,
        setCurrentVideoId: handleSetCurrentVideoId,
        refreshStatus,
        refreshScenes,
      }}
    >
      {children}
    </VideoContext.Provider>
  );
}
