"use client";

import { Play } from "lucide-react";

interface VideoPlayerProps {
  videoUrl?: string;
}

export function VideoPlayer({ videoUrl }: VideoPlayerProps) {
  // If we have a video URL, show the actual video player
  if (videoUrl) {
    return (
      <div className="w-full h-full relative">
        <video
          src={videoUrl}
          controls
          className="w-full h-full object-contain bg-black"
          autoPlay
        >
          Your browser does not support the video tag.
        </video>
      </div>
    );
  }

  // Placeholder state when no video is available
  return (
    <div className="w-full h-full relative group">
      {/* Placeholder Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-950 to-black opacity-100" />
      
      {/* Grid Pattern */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: "radial-gradient(circle, #ffffff 1px, transparent 1px)",
          backgroundSize: "24px 24px",
        }}
      />

      {/* Play Button */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="h-16 w-16 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 flex items-center justify-center text-white shadow-2xl">
          <Play className="h-8 w-8 ml-1 fill-white/30 text-white/30" />
        </div>
      </div>

      {/* Status Overlay */}
      <div className="absolute bottom-4 left-4 right-4">
        <div className="bg-black/40 backdrop-blur-md rounded px-3 py-2 border border-white/5">
          <p className="text-gray-400 text-xs text-center">
            Video will appear here once rendering is complete
          </p>
        </div>
      </div>
    </div>
  );
}
