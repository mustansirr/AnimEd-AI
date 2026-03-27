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
} from "lucide-react";
import { useVideo } from "./VideoContext";
import { approveScripts, SceneResponse, ApiError } from "@/lib/api";

interface ScriptReviewProps {
  onClose?: () => void;
}

export function ScriptReview({ onClose }: ScriptReviewProps) {
  const { currentVideoId, scenes, videoStatus, refreshStatus } = useVideo();
  const [feedback, setFeedback] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<{
    status: "idle" | "success" | "error";
    message: string;
  }>({ status: "idle", message: "" });

  const isWaitingApproval = videoStatus === "waiting_approval";

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
      // Refresh status to update pipeline
      await refreshStatus();
      // Close after a short delay if approved
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

  return (
    <Card className="border shadow-sm bg-white max-h-[70vh] overflow-hidden flex flex-col">
      <CardHeader className="pb-3 border-b bg-gray-50/50 flex-shrink-0">
        <CardTitle className="text-base font-semibold flex justify-between items-center">
          <span className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-[#F875AA]" />
            Review Generated Scripts
          </span>
          <span className="text-xs font-normal text-muted-foreground">
            {scenes.length} scene{scenes.length !== 1 ? "s" : ""}
          </span>
        </CardTitle>
      </CardHeader>

      <CardContent className="p-4 space-y-4 overflow-y-auto flex-1">
        {/* Scene Cards */}
        {scenes.map((scene: SceneResponse) => (
          <div
            key={scene.id}
            className="border rounded-lg p-4 bg-gray-50/50 space-y-3"
          >
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-sm">
                Scene {scene.scene_order}
              </h4>
            </div>

            {scene.narration_script && (
              <div>
                <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1 flex items-center gap-1">
                  <MessageSquare className="w-3 h-3" />
                  Narration
                </p>
                <p className="text-sm text-gray-700 bg-white p-2 rounded border">
                  {scene.narration_script}
                </p>
              </div>
            )}

            {scene.visual_plan && (
              <div>
                <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1 flex items-center gap-1">
                  <Eye className="w-3 h-3" />
                  Visual Plan
                </p>
                <p className="text-sm text-gray-700 bg-white p-2 rounded border font-mono">
                  {scene.visual_plan}
                </p>
              </div>
            )}
          </div>
        ))}

        {/* Feedback Section */}
        {isWaitingApproval && (
          <div className="space-y-2 pt-2 border-t">
            <label className="text-xs font-medium text-muted-foreground">
              Feedback (required for rejection)
            </label>
            <Textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Provide feedback if you want changes..."
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
        <div className="p-4 border-t bg-gray-50/50 flex gap-2 justify-end flex-shrink-0">
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
        </div>
      )}
    </Card>
  );
}
