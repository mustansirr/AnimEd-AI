"use client";

import { useEffect, useState, useCallback } from "react";
import { createClient } from "@/utils/supabase/client";
import { listUserVideos, deleteVideo, VideoStatusResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Play,
  Trash2,
  Loader2,
  VideoOff,
  X,
  AlertTriangle,
} from "lucide-react";
import Link from "next/link";
import { VideoDetailModal } from "./VideoDetailModal";

// =============================================================================
// Types
// =============================================================================

interface VideoItem extends VideoStatusResponse {
  // Extend if needed in the future
}

// =============================================================================
// Status Badge Component
// =============================================================================

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { label: string; className: string }> = {
    completed: {
      label: "Completed",
      className: "bg-green-100 text-green-700",
    },
    failed: {
      label: "Failed",
      className: "bg-red-100 text-red-700",
    },
    planning: {
      label: "Planning",
      className: "bg-blue-100 text-blue-700",
    },
    scripting: {
      label: "Scripting",
      className: "bg-purple-100 text-purple-700",
    },
    waiting_approval: {
      label: "Awaiting Approval",
      className: "bg-yellow-100 text-yellow-700",
    },
    generating: {
      label: "Generating",
      className: "bg-indigo-100 text-indigo-700",
    },
    rendering: {
      label: "Rendering",
      className: "bg-orange-100 text-orange-700",
    },
    stitching: {
      label: "Stitching",
      className: "bg-teal-100 text-teal-700",
    },
  };

  const { label, className } = config[status] ?? {
    label: status,
    className: "bg-gray-100 text-gray-700",
  };

  return (
    <span
      className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full ${className}`}
    >
      {label}
    </span>
  );
}

// =============================================================================
// Video Card Component
// =============================================================================

function VideoCard({
  video,
  onPlay,
  onDelete,
  onSelect,
  isDeleting,
}: {
  video: VideoItem;
  onPlay: (video: VideoItem) => void;
  onDelete: (videoId: string) => void;
  onSelect: (video: VideoItem) => void;
  isDeleting: boolean;
}) {
  const hasVideo = !!video.final_video_url;
  const createdAt = new Date(video.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="group bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow cursor-pointer" onClick={() => onSelect(video)}>
      {/* Thumbnail / Preview */}
      <div
        className="relative aspect-video bg-gradient-to-br from-indigo-950 to-gray-900"
      >
        {hasVideo ? (
          <>
            <video
              src={video.final_video_url}
              className="w-full h-full object-cover"
              preload="metadata"
              muted
            />
            <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <div
                className="h-12 w-12 rounded-full bg-white/20 backdrop-blur-sm border border-white/30 flex items-center justify-center"
                onClick={(e) => {
                  e.stopPropagation();
                  onPlay(video);
                }}
              >
                <Play className="h-6 w-6 ml-0.5 text-white fill-white" />
              </div>
            </div>
          </>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <VideoOff className="h-8 w-8 text-gray-500 mx-auto mb-2" />
              <p className="text-xs text-gray-400">No video yet</p>
            </div>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-3">
        <div className="flex items-start justify-between gap-2 mb-2">
          <p
            className="text-sm font-medium text-gray-800 line-clamp-2 flex-1"
            title={video.prompt}
          >
            {video.prompt}
          </p>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <StatusBadge status={video.status} />
            <span className="text-xs text-gray-400">{createdAt}</span>
          </div>

          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-gray-400 hover:text-red-600 hover:bg-red-50"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(video.id);
            }}
            disabled={isDeleting}
          >
            {isDeleting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Video Player Modal
// =============================================================================

function VideoPlayerModal({
  video,
  onClose,
}: {
  video: VideoItem;
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-4xl bg-black rounded-lg overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-2 right-2 z-10 text-white hover:bg-white/20"
          onClick={onClose}
        >
          <X className="h-5 w-5" />
        </Button>

        <video
          src={video.final_video_url}
          controls
          autoPlay
          className="w-full aspect-video"
        >
          Your browser does not support the video tag.
        </video>

        <div className="p-4">
          <p className="text-sm text-gray-300">{video.prompt}</p>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Delete Confirmation Dialog
// =============================================================================

function DeleteConfirmDialog({
  onConfirm,
  onCancel,
  isDeleting,
}: {
  onConfirm: () => void;
  onCancel: () => void;
  isDeleting: boolean;
}) {
  return (
    <div
      className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
      onClick={onCancel}
    >
      <div
        className="bg-white rounded-lg p-6 max-w-sm w-full shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center">
            <AlertTriangle className="h-5 w-5 text-red-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Delete Video
            </h3>
            <p className="text-sm text-gray-500">
              This action cannot be undone.
            </p>
          </div>
        </div>

        <p className="text-sm text-gray-600 mb-6">
          Are you sure you want to delete this video? All associated data
          including scenes will be permanently removed.
        </p>

        <div className="flex justify-end gap-3">
          <Button variant="ghost" onClick={onCancel} disabled={isDeleting}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={onConfirm}
            disabled={isDeleting}
            className="bg-red-600 hover:bg-red-700"
          >
            {isDeleting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Deleting…
              </>
            ) : (
              "Delete"
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Skeleton Loader
// =============================================================================

function SkeletonCard() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden animate-pulse">
      <div className="aspect-video bg-gray-200" />
      <div className="p-3 space-y-2">
        <div className="h-4 bg-gray-200 rounded w-3/4" />
        <div className="flex items-center justify-between">
          <div className="h-5 bg-gray-200 rounded-full w-20" />
          <div className="h-8 w-8 bg-gray-200 rounded" />
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Main VideoGrid Component
// =============================================================================

export function VideoGrid() {
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [playingVideo, setPlayingVideo] = useState<VideoItem | null>(null);
  const [deletingVideoId, setDeletingVideoId] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);
  const [selectedVideo, setSelectedVideo] = useState<VideoItem | null>(null);

  const fetchVideos = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const supabase = createClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) {
        setError("Not authenticated");
        return;
      }

      const data = await listUserVideos(user.id);
      setVideos(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load videos");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchVideos();
  }, [fetchVideos]);

  const handleDelete = async () => {
    if (!confirmDeleteId) return;

    try {
      setDeletingVideoId(confirmDeleteId);
      await deleteVideo(confirmDeleteId);
      setVideos((prev) => prev.filter((v) => v.id !== confirmDeleteId));
      setConfirmDeleteId(null);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to delete video"
      );
    } finally {
      setDeletingVideoId(null);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center mb-4">
          <AlertTriangle className="h-6 w-6 text-red-600" />
        </div>
        <p className="text-sm text-gray-600 mb-4">{error}</p>
        <Button variant="outline" onClick={fetchVideos}>
          Try Again
        </Button>
      </div>
    );
  }

  // Empty state
  if (videos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="h-16 w-16 rounded-full bg-gray-100 flex items-center justify-center mb-4">
          <VideoOff className="h-8 w-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-1">
          No videos yet
        </h3>
        <p className="text-sm text-gray-500 mb-6 max-w-sm">
          Head to the Dashboard to create your first educational video with AI.
        </p>
        <Link href="/dashboard">
          <Button>Go to Dashboard</Button>
        </Link>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {videos.map((video) => (
          <VideoCard
            key={video.id}
            video={video}
            onPlay={setPlayingVideo}
            onDelete={setConfirmDeleteId}
            onSelect={setSelectedVideo}
            isDeleting={deletingVideoId === video.id}
          />
        ))}
      </div>

      {/* Video Player Modal */}
      {playingVideo && (
        <VideoPlayerModal
          video={playingVideo}
          onClose={() => setPlayingVideo(null)}
        />
      )}

      {/* Delete Confirmation Dialog */}
      {confirmDeleteId && (
        <DeleteConfirmDialog
          onConfirm={handleDelete}
          onCancel={() => setConfirmDeleteId(null)}
          isDeleting={!!deletingVideoId}
        />
      )}

      {/* Video Detail Modal */}
      {selectedVideo && (
        <VideoDetailModal
          videoId={selectedVideo.id}
          videoStatus={selectedVideo.status}
          videoPrompt={selectedVideo.prompt}
          onClose={() => {
            setSelectedVideo(null);
            // Refresh the list in case status changed (e.g. approved scripts)
            fetchVideos();
          }}
        />
      )}
    </>
  );
}
