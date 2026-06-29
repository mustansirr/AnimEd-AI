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
  Film,
  X,
  AlertTriangle,
  Download,
  Search,
  Filter,
} from "lucide-react";
import Link from "next/link";
import { VideoWorkspace } from "./VideoWorkspace";
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
      className: "bg-[#FFDFDF] text-[#e8609a]",
    },
    waiting_approval: {
      label: "Awaiting Approval",
      className: "bg-yellow-100 text-yellow-700",
    },
    generating: {
      label: "Generating",
      className: "bg-[#FFDFDF] text-[#e8609a]",
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
    <div className="group bg-white dark:bg-card rounded-lg border border-gray-200 dark:border-border overflow-hidden shadow-sm hover:shadow-md transition-shadow cursor-pointer" onClick={() => onSelect(video)}>
      {/* Thumbnail / Preview */}
      <div
        className="relative aspect-video bg-gradient-to-br from-[#F875AA]/20 to-gray-900"
      >
        {hasVideo ? (
          <>
            <video
              src={`${video.final_video_url}#t=2.0`}
              className="w-full h-full object-cover"
              preload="metadata"
              muted
            />
            
            <div 
              className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-center cursor-pointer backdrop-blur-[2px]"
              onClick={(e) => {
                e.stopPropagation();
                onPlay(video);
              }}
            >
              <div
                className="h-14 w-14 rounded-full bg-pink-500 shadow-lg shadow-pink-500/40 flex items-center justify-center transform scale-90 group-hover:scale-100 transition-transform duration-300"
              >
                <Play className="h-6 w-6 ml-1 text-white fill-white" />
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
            className="text-sm font-medium text-gray-800 dark:text-card-foreground line-clamp-2 flex-1"
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
        className="relative w-full max-w-4xl bg-black rounded-lg overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 bg-gray-900 border-b border-gray-800">
          <h2 className="text-white font-medium text-lg truncate pr-4">{video.prompt}</h2>
          <div className="flex items-center gap-2">
            <a 
              href={video.final_video_url} 
              download={`video_${video.id}.mp4`}
              target="_blank"
              rel="noreferrer"
            >
              <Button variant="outline" size="sm" className="h-8 gap-2 bg-gray-800 text-white border-gray-700 hover:bg-gray-700">
                <Download className="w-4 h-4" />
                Download
              </Button>
            </a>
            <Button
              variant="ghost"
              size="icon"
              className="text-gray-400 hover:text-white hover:bg-gray-800 h-8 w-8"
              onClick={onClose}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>

        <video
          src={video.final_video_url}
          controls
          autoPlay
          className="w-full aspect-video bg-black"
        >
          Your browser does not support the video tag.
        </video>
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
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={onCancel}
    >
      <div
        className="bg-white dark:bg-card rounded-lg p-6 max-w-sm w-full shadow-xl border border-gray-200 dark:border-border"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
            <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-foreground">
              Delete Video
            </h3>
            <p className="text-sm text-gray-500 dark:text-muted-foreground">
              This action cannot be undone.
            </p>
          </div>
        </div>

        <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">
          Are you sure you want to delete this video? All associated data
          including scenes will be permanently removed.
        </p>

        <div className="flex justify-end gap-3">
          <Button variant="ghost" onClick={onCancel} disabled={isDeleting} className="text-gray-700 dark:text-foreground hover:bg-gray-100 dark:hover:bg-muted">
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
    <div className="bg-white dark:bg-card rounded-lg border border-gray-200 dark:border-border overflow-hidden animate-pulse">
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
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const fetchVideos = useCallback(async (showLoader: boolean = true) => {
    try {
      if (showLoader) setLoading(true);
      if (showLoader) setError(null);

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
      if (showLoader) setError(err instanceof Error ? err.message : "Failed to load videos");
    } finally {
      if (showLoader) setLoading(false);
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
        <Button variant="outline" onClick={() => fetchVideos()}>
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

  const filteredVideos = videos.filter((video) => {
    const matchesSearch = video.prompt?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false;
    const matchesStatus = statusFilter === "all" || video.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (selectedVideo) {
    return (
      <VideoWorkspace
        video={selectedVideo}
        onBack={() => {
          setSelectedVideo(null);
          // Refresh the list silently
          fetchVideos(false);
        }}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 items-center bg-white dark:bg-card p-2 rounded-xl border border-gray-100 dark:border-border shadow-[0_2px_10px_-3px_rgba(0,0,0,0.05)]">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search your generated videos..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-3 border-none bg-transparent rounded-lg text-sm text-gray-700 dark:text-foreground placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#F875AA]/20 transition-all"
          />
        </div>
        
        <div className="w-px h-8 bg-gray-100 dark:bg-border hidden sm:block"></div>
        
        <div className="relative w-full sm:w-auto min-w-[200px]">
          <div className="absolute left-3 top-1/2 -translate-y-1/2 flex items-center pointer-events-none">
            <Filter className="h-4 w-4 text-gray-500 dark:text-muted-foreground" />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full appearance-none pl-9 pr-10 py-3 bg-gray-50 dark:bg-muted hover:bg-gray-100/80 dark:hover:bg-muted/80 border border-gray-100 dark:border-border text-gray-700 dark:text-muted-foreground text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-[#F875AA]/20 transition-colors cursor-pointer"
          >
            <option value="all">All Statuses</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="waiting_approval">Awaiting Approval</option>
          </select>
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
          </div>
        </div>
      </div>

      {filteredVideos.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center bg-white dark:bg-card rounded-lg border border-gray-200 dark:border-border shadow-sm">
          <Search className="h-12 w-12 text-gray-300 dark:text-muted-foreground/30 mb-4" />
          <p className="text-gray-500 dark:text-muted-foreground font-medium">No videos match your search</p>
          <Button variant="link" onClick={() => { setSearchQuery(""); setStatusFilter("all"); }} className="text-[#F875AA]">
            Clear filters
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredVideos.map((video) => (
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
      )}

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


    </div>
  );
}
