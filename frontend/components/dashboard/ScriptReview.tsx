"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Check,
  X,
  Loader2,
  FileText,
  Eye,
  MessageSquare,
  Pencil,
  RotateCcw,
  Send,
} from "lucide-react";
import { useVideo } from "./VideoContext";
import { approveScripts, SceneResponse, ApiError } from "@/lib/api";

interface ScriptReviewProps {
  onClose?: () => void;
}

interface SceneEdits {
  narration_script: string;
  visual_plan: string;
}

export function ScriptReview({ onClose }: ScriptReviewProps) {
  const { currentVideoId, scenes, videoStatus, refreshStatus } = useVideo();
  const [feedback, setFeedback] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<{
    status: "idle" | "success" | "error";
    message: string;
  }>({ status: "idle", message: "" });

  // ── Suggest-Edits state ──────────────────────────────────────────────────
  const [isSuggestMode, setIsSuggestMode] = useState(false);
  /** Per-scene editable copies; keyed by scene.id */
  const [sceneEdits, setSceneEdits] = useState<Record<string, SceneEdits>>({});

  const isWaitingApproval = videoStatus === "waiting_approval";

  // ── Helpers ──────────────────────────────────────────────────────────────

  /** Enter suggest-edits mode: seed editable copies from current scenes */
  const enterSuggestMode = () => {
    const initial: Record<string, SceneEdits> = {};
    scenes.forEach((s) => {
      initial[s.id] = {
        narration_script: s.narration_script ?? "",
        visual_plan: s.visual_plan ?? "",
      };
    });
    setSceneEdits(initial);
    setIsSuggestMode(true);
    setResult({ status: "idle", message: "" });
  };

  const cancelSuggestMode = () => {
    setIsSuggestMode(false);
    setSceneEdits({});
    setResult({ status: "idle", message: "" });
  };

  const updateSceneEdit = (
    sceneId: string,
    field: keyof SceneEdits,
    value: string
  ) => {
    setSceneEdits((prev) => ({
      ...prev,
      [sceneId]: { ...prev[sceneId], [field]: value },
    }));
  };

  const resetSceneEdit = (scene: SceneResponse) => {
    setSceneEdits((prev) => ({
      ...prev,
      [scene.id]: {
        narration_script: scene.narration_script ?? "",
        visual_plan: scene.visual_plan ?? "",
      },
    }));
  };

  // ── Submit helpers ───────────────────────────────────────────────────────

  const handleApprove = async () => {
    if (!currentVideoId) return;
    await submitApproval(true);
  };

  const handleReject = async () => {
    if (!currentVideoId || !feedback.trim()) {
      setResult({
        status: "error",
        message: "Please provide feedback when rejecting scripts.",
      });
      return;
    }
    await submitApproval(false);
  };

  /** Build a human-readable diff of user edits and submit as rejection feedback */
  const handleSubmitSuggestions = async () => {
    if (!currentVideoId) return;

    // Build structured suggestion text
    const diffLines: string[] = ["=== Suggested Edits ===\n"];
    scenes.forEach((scene) => {
      const edits = sceneEdits[scene.id];
      if (!edits) return;

      const narrationChanged =
        edits.narration_script !== (scene.narration_script ?? "");
      const visualChanged = edits.visual_plan !== (scene.visual_plan ?? "");

      if (!narrationChanged && !visualChanged) return;

      diffLines.push(`--- Scene ${scene.scene_order} ---`);
      if (narrationChanged) {
        diffLines.push(`[Narration – Original]:\n${scene.narration_script ?? "(empty)"}`);
        diffLines.push(`[Narration – Suggested]:\n${edits.narration_script}`);
      }
      if (visualChanged) {
        diffLines.push(`[Visual Plan – Original]:\n${scene.visual_plan ?? "(empty)"}`);
        diffLines.push(`[Visual Plan – Suggested]:\n${edits.visual_plan}`);
      }
      diffLines.push("");
    });

    const hasAnyChange = diffLines.length > 1;
    if (!hasAnyChange && !feedback.trim()) {
      setResult({
        status: "error",
        message: "Please make at least one edit or add feedback before submitting suggestions.",
      });
      return;
    }

    const combinedFeedback = [
      ...diffLines,
      feedback.trim() ? `\n=== Additional Notes ===\n${feedback.trim()}` : "",
    ]
      .join("\n")
      .trim();

    setIsSubmitting(true);
    setResult({ status: "idle", message: "" });

    try {
      const response = await approveScripts(
        currentVideoId,
        false, // treat suggestions as a rejection → triggers re-generation
        combinedFeedback
      );
      setResult({
        status: "success",
        message: response.message || "Suggestions submitted! Scripts will be regenerated.",
      });
      await refreshStatus();
      setIsSuggestMode(false);
      setSceneEdits({});
    } catch (err) {
      setResult({
        status: "error",
        message: err instanceof ApiError ? err.message : "Failed to submit suggestions",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitApproval = async (approved: boolean) => {
    if (!currentVideoId) return;

    setIsSubmitting(true);
    setResult({ status: "idle", message: "" });

    try {
      const response = await approveScripts(
        currentVideoId,
        approved,
        feedback || undefined
      );
      setResult({
        status: "success",
        message: response.message,
      });
      await refreshStatus();
      if (approved && onClose) {
        setTimeout(onClose, 1500);
      }
    } catch (err) {
      setResult({
        status: "error",
        message: err instanceof ApiError ? err.message : "Failed to submit",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // ── Empty state ──────────────────────────────────────────────────────────

  if (scenes.length === 0) {
    return (
      <Card className="border shadow-sm bg-white">
        <CardContent className="p-6 text-center text-muted-foreground">
          <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No scripts generated yet.</p>
        </CardContent>
      </Card>
    );
  }

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <Card className="border shadow-sm bg-white max-h-[70vh] overflow-hidden flex flex-col">
      <CardHeader className="pb-3 border-b bg-gray-50/50 flex-shrink-0">
        <CardTitle className="text-base font-semibold flex justify-between items-center">
          <span className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-[#F875AA]" />
            Review Generated Scripts
            {isSuggestMode && (
              <span className="text-xs font-normal text-amber-600 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                Edit Mode
              </span>
            )}
          </span>
          <span className="text-xs font-normal text-muted-foreground">
            {scenes.length} scene{scenes.length !== 1 ? "s" : ""}
          </span>
        </CardTitle>
      </CardHeader>

      <CardContent className="p-4 space-y-4 overflow-y-auto flex-1">
        {/* Scene Cards */}
        {scenes.map((scene: SceneResponse) => {
          const edits = sceneEdits[scene.id];
          return (
            <div
              key={scene.id}
              className={`border rounded-lg p-4 space-y-3 transition-colors ${
                isSuggestMode
                  ? "bg-amber-50/40 border-amber-200"
                  : "bg-gray-50/50"
              }`}
            >
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-sm">
                  Scene {scene.scene_order}
                </h4>
                {isSuggestMode && (
                  <button
                    type="button"
                    onClick={() => resetSceneEdit(scene)}
                    className="flex items-center gap-1 text-[10px] text-muted-foreground hover:text-amber-600 transition-colors"
                    title="Reset this scene to original"
                  >
                    <RotateCcw className="w-3 h-3" />
                    Reset
                  </button>
                )}
              </div>

              {/* Narration */}
              {(scene.narration_script || isSuggestMode) && (
                <div>
                  <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1 flex items-center gap-1">
                    <MessageSquare className="w-3 h-3" />
                    Narration
                  </p>
                  {isSuggestMode ? (
                    <Textarea
                      value={edits?.narration_script ?? ""}
                      onChange={(e) =>
                        updateSceneEdit(scene.id, "narration_script", e.target.value)
                      }
                      className="text-sm min-h-[80px] resize-y border-amber-300 focus-visible:ring-amber-400 bg-white"
                      placeholder="Edit narration script…"
                    />
                  ) : (
                    <p className="text-sm text-gray-700 bg-white p-2 rounded border">
                      {scene.narration_script}
                    </p>
                  )}
                </div>
              )}

              {/* Visual Plan */}
              {(scene.visual_plan || isSuggestMode) && (
                <div>
                  <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1 flex items-center gap-1">
                    <Eye className="w-3 h-3" />
                    Visual Plan
                  </p>
                  {isSuggestMode ? (
                    <Textarea
                      value={edits?.visual_plan ?? ""}
                      onChange={(e) =>
                        updateSceneEdit(scene.id, "visual_plan", e.target.value)
                      }
                      className="text-sm min-h-[80px] resize-y font-mono border-amber-300 focus-visible:ring-amber-400 bg-white"
                      placeholder="Edit visual plan…"
                    />
                  ) : (
                    <p className="text-sm text-gray-700 bg-white p-2 rounded border font-mono">
                      {scene.visual_plan}
                    </p>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {/* Feedback / Notes Section */}
        {isWaitingApproval && (
          <div className="space-y-2 pt-2 border-t">
            <label className="text-xs font-medium text-muted-foreground">
              {isSuggestMode
                ? "Additional notes (optional)"
                : "Feedback (required for rejection)"}
            </label>
            <Textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder={
                isSuggestMode
                  ? "Any extra context for your suggested edits…"
                  : "Provide feedback if you want changes..."
              }
              className="min-h-[60px] resize-none text-sm"
            />
          </div>
        )}

        {/* Result Message */}
        {result.status !== "idle" && (
          <div
            className={`text-xs p-2 rounded-md flex items-center gap-2 ${
              result.status === "success"
                ? "bg-green-50 text-green-700 border border-green-100"
                : "bg-red-50 text-red-700 border border-red-100"
            }`}
          >
            {result.status === "success" ? (
              <Check className="w-3 h-3" />
            ) : (
              <X className="w-3 h-3" />
            )}
            {result.message}
          </div>
        )}
      </CardContent>

      {/* Action Buttons */}
      {isWaitingApproval && (
        <div className="p-4 border-t bg-gray-50/50 flex gap-2 justify-end flex-shrink-0 flex-wrap">
          {isSuggestMode ? (
            /* ── Suggest-mode actions ── */
            <>
              <Button
                variant="outline"
                size="sm"
                className="gap-2 text-muted-foreground hover:text-gray-700"
                onClick={cancelSuggestMode}
                disabled={isSubmitting}
              >
                <X className="w-3 h-3" />
                Cancel
              </Button>
              <Button
                size="sm"
                className="gap-2 bg-amber-500 hover:bg-amber-600 text-white"
                onClick={handleSubmitSuggestions}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <Send className="w-3 h-3" />
                )}
                Submit Suggestions
              </Button>
            </>
          ) : (
            /* ── Normal review actions ── */
            <>
              <Button
                variant="outline"
                size="sm"
                className="gap-2 text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={handleReject}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <X className="w-3 h-3" />
                )}
                Reject
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="gap-2 text-amber-600 hover:text-amber-700 hover:bg-amber-50 border-amber-300"
                onClick={enterSuggestMode}
                disabled={isSubmitting}
              >
                <Pencil className="w-3 h-3" />
                Suggest Edits
              </Button>
              <Button
                size="sm"
                className="gap-2 bg-green-600 hover:bg-green-700 text-white"
                onClick={handleApprove}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <Check className="w-3 h-3" />
                )}
                Approve Scripts
              </Button>
            </>
          )}
        </div>
      )}
    </Card>
  );
}
