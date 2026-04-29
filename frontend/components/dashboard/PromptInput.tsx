"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Paperclip, Sparkles, Loader2, Check, X } from "lucide-react";
import { createClient } from "@/utils/supabase/client";
import { createVideo, uploadPdf, startWorkflow, ApiError } from "@/lib/api";
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
      // Step 1: Create video record (does NOT start workflow yet)
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

      // Step 3: Start the workflow AFTER PDF embeddings are stored
      // This ensures the planner agent has RAG context available
      const workflowResult = await startWorkflow(result.video_id);

      setGenerationResult({
        status: "success",
        message: workflowResult.message,
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
    <div className="w-full max-w-3xl mx-auto">
      {/* Prompt box with inline actions */}
      <div className="relative rounded-xl border border-gray-200 bg-white shadow-sm focus-within:ring-2 focus-within:ring-[#F875AA]/20 focus-within:border-[#F875AA]/40 transition-all">
        <Textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., Explain Quantum Entanglement using a soccer metaphor..."
          className="min-h-[140px] max-h-[240px] resize-none border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-base px-5 pt-5 pb-14"
        />

        {/* Bottom bar inside the textarea box */}
        <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between px-3 py-2">
          <div className="flex items-center gap-2">
            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
            />
            <button
              type="button"
              className={`p-1.5 rounded-md transition-colors ${
                uploadState.file
                  ? "text-[#e8609a] bg-[#FFF6F6]"
                  : "text-gray-400 hover:text-gray-600 hover:bg-gray-100"
              }`}
              onClick={handleUploadClick}
              disabled={isGenerating}
              title={uploadState.file ? uploadState.file.name : "Attach PDF"}
            >
              {uploadState.status === "uploading" ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : uploadState.status === "success" ? (
                <Check className="w-4 h-4 text-green-600" />
              ) : (
                <Paperclip className="w-4 h-4" />
              )}
            </button>
            {uploadState.file && (
              <span className="text-[11px] text-gray-500 truncate max-w-[150px]">
                {uploadState.file.name}
              </span>
            )}
          </div>

          <Button
            size="sm"
            className="bg-[#F875AA] hover:bg-[#e8609a] text-white shadow-sm transition-all gap-1.5 text-xs h-8 px-4 rounded-lg disabled:opacity-50"
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
      </div>

      {/* Status Messages */}
      {generationResult.status !== "idle" && (
        <div
          className={`mt-3 text-xs p-2.5 rounded-lg flex items-center gap-2 ${
            generationResult.status === "success"
              ? "bg-green-50 text-green-700 border border-green-100"
              : "bg-red-50 text-red-700 border border-red-100"
          }`}
        >
          {generationResult.status === "success" ? (
            <Check className="w-3 h-3 flex-shrink-0" />
          ) : (
            <X className="w-3 h-3 flex-shrink-0" />
          )}
          {generationResult.message}
        </div>
      )}

      {/* Upload status message */}
      {uploadState.message && uploadState.status === "error" && (
        <p className="mt-2 text-[11px] text-red-500 text-center">
          {uploadState.message}
        </p>
      )}
    </div>
  );
}
