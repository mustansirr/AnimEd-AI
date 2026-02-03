"use client";

import { useState, useRef, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Upload, Sparkles, Link, Loader2, Check, X } from "lucide-react";
import { createClient } from "@/utils/supabase/client";
import { createVideo, uploadPdf, ApiError } from "@/lib/api";
import { useVideo } from "./VideoContext";

interface UploadState {
  file: File | null;
  status: "idle" | "uploading" | "success" | "error";
  message: string;
}

export function PromptInput() {
  const { setCurrentVideoId } = useVideo();
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>({
    file: null,
    status: "idle",
    message: "",
  });
  const [generationResult, setGenerationResult] = useState<{
    status: "idle" | "success" | "error";
    message: string;
    videoId?: string;
  }>({ status: "idle", message: "" });

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Get user ID on mount
  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (user) {
        setUserId(user.id);
      }
    });
  }, []);

  // Validation: Generate is enabled only if prompt has content
  const canGenerate = prompt.trim().length > 0 && !isGenerating;

  const handleClear = () => {
    setPrompt("");
    setUploadState({ file: null, status: "idle", message: "" });
    setGenerationResult({ status: "idle", message: "" });
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        setUploadState({
          file: null,
          status: "error",
          message: "Only PDF files are supported",
        });
        return;
      }
      setUploadState({
        file,
        status: "idle",
        message: `Selected: ${file.name}`,
      });
    }
  };

  const handleGenerate = async () => {
    if (!canGenerate || !userId) return;

    setIsGenerating(true);
    setGenerationResult({ status: "idle", message: "" });

    try {
      // Step 1: Create video request (triggers workflow)
      const result = await createVideo(prompt, userId);
      
      // Step 2: If PDF is selected, upload it for RAG context
      if (uploadState.file && result.video_id) {
        setUploadState((prev) => ({ ...prev, status: "uploading" }));
        try {
          const uploadResult = await uploadPdf(uploadState.file, result.video_id);
          setUploadState({
            file: uploadState.file,
            status: "success",
            message: `PDF processed: ${uploadResult.chunks_stored} chunks stored`,
          });
        } catch (uploadError) {
          // PDF upload failed but video was created
          const errorMsg = uploadError instanceof ApiError 
            ? uploadError.message 
            : "PDF upload failed";
          setUploadState((prev) => ({
            ...prev,
            status: "error",
            message: errorMsg,
          }));
        }
      }

      setGenerationResult({
        status: "success",
        message: result.message,
        videoId: result.video_id,
      });

      // Set video ID in context to trigger pipeline polling
      setCurrentVideoId(result.video_id);
    } catch (error) {
      const errorMsg = error instanceof ApiError 
        ? error.message 
        : "Failed to generate video";
      setGenerationResult({
        status: "error",
        message: errorMsg,
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Card className="h-full border shadow-sm bg-white">
      <CardContent className="p-4 space-y-4">
        {/* Header/Title Area */}
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-sm flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-500" />
            What&apos;s today&apos;s lesson or concept?
          </h3>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 text-[10px] text-muted-foreground hover:text-red-500"
            onClick={handleClear}
          >
            Clear
          </Button>
        </div>

        {/* Text Area */}
        <Textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={`Topic: Introduction to Gravity for high school students.\nTone: Engaging, slightly humorous but educational.\nKey points to cover:\n1. Newton's Apple myth vs reality.\n...`}
          className="min-h-[120px] resize-none border-gray-100 bg-gray-50/50 focus-visible:ring-1 focus-visible:ring-indigo-500 font-mono text-sm"
        />

        {/* Status Messages */}
        {generationResult.status !== "idle" && (
          <div
            className={`text-xs p-2 rounded-md flex items-center gap-2 ${
              generationResult.status === "success"
                ? "bg-green-50 text-green-700 border border-green-100"
                : "bg-red-50 text-red-700 border border-red-100"
            }`}
          >
            {generationResult.status === "success" ? (
              <Check className="w-3 h-3" />
            ) : (
              <X className="w-3 h-3" />
            )}
            {generationResult.message}
          </div>
        )}

        {/* Action Footer */}
        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center gap-2">
            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
            />
            <Button
              variant="outline"
              size="sm"
              className={`h-8 text-xs gap-2 ${
                uploadState.status === "success"
                  ? "bg-green-50 border-green-200 text-green-700"
                  : uploadState.status === "error"
                  ? "bg-red-50 border-red-200 text-red-700"
                  : "bg-gray-50"
              }`}
              onClick={handleUploadClick}
              disabled={isGenerating}
            >
              {uploadState.status === "uploading" ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : uploadState.status === "success" ? (
                <Check className="w-3 h-3" />
              ) : (
                <Upload className="w-3 h-3" />
              )}
              {uploadState.file ? uploadState.file.name.slice(0, 20) : "Upload PDF"}
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-8 text-xs gap-2 bg-gray-50"
              disabled
            >
              <Link className="w-3 h-3" />
              Add URL
            </Button>
          </div>

          <Button
            size="sm"
            className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition-all gap-2 text-xs h-8 disabled:opacity-50"
            onClick={handleGenerate}
            disabled={!canGenerate}
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin" />
                Generating...
              </>
            ) : (
              "Generate"
            )}
          </Button>
        </div>

        {/* Upload status message */}
        {uploadState.message && uploadState.status !== "idle" && (
          <p
            className={`text-[10px] ${
              uploadState.status === "error" ? "text-red-500" : "text-muted-foreground"
            }`}
          >
            {uploadState.message}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
