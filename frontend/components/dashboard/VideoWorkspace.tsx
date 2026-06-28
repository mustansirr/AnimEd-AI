"use client";

import { useEffect, useState, useRef } from "react";
import { getScenes, SceneResponse, sendChatMessage } from "@/lib/api";
import { createClient } from "@/utils/supabase/client";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Send, Loader2, PlaySquare, FileText, MessageSquare } from "lucide-react";
import ReactMarkdown from 'react-markdown';

interface VideoWorkspaceProps {
  video: {
    id: string;
    prompt: string;
    final_video_url?: string;
  };
  onBack: () => void;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export function VideoWorkspace({ video, onBack }: VideoWorkspaceProps) {
  const [scenes, setScenes] = useState<SceneResponse[]>([]);
  const [loadingScenes, setLoadingScenes] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchScenes = async () => {
      try {
        setLoadingScenes(true);
        const data = await getScenes(video.id);
        // Sort by scene_order just in case
        data.sort((a, b) => a.scene_order - b.scene_order);
        setScenes(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load scenes");
      } finally {
        setLoadingScenes(false);
      }
    };
    fetchScenes();
  }, [video.id]);

  useEffect(() => {
    // Scroll to bottom of chat when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isSending) return;

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsSending(true);

    try {
      const supabase = createClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) throw new Error("Not authenticated");

      const response = await sendChatMessage(video.id, user.id, userMessage);
      setMessages((prev) => [...prev, { role: "assistant", content: response.answer }]);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error while trying to answer that." },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-[#FFF6F6] dark:bg-background rounded-xl overflow-hidden shadow-sm border border-gray-200 dark:border-border">
      {/* Header */}
      <div className="flex items-center p-4 bg-white dark:bg-card border-b border-gray-200 dark:border-border shrink-0">
        <Button variant="ghost" size="icon" onClick={onBack} className="mr-3 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-foreground">
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-foreground line-clamp-1">{video.prompt}</h2>
          <p className="text-xs text-gray-500 dark:text-muted-foreground">Video Workspace</p>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden flex-col lg:flex-row">
        {/* Left Column (Video & Script) */}
        <div className="flex flex-col w-full lg:w-2/3 border-b lg:border-b-0 lg:border-r border-gray-200 dark:border-border h-full overflow-hidden">
          
          {/* Top: Video Player */}
          <div className="w-full bg-black flex items-center justify-center shrink-0" style={{ maxHeight: '50vh' }}>
            {video.final_video_url ? (
              <video
                src={video.final_video_url}
                controls
                className="w-full h-full object-contain"
                style={{ maxHeight: '50vh' }}
              />
            ) : (
              <div className="flex flex-col items-center justify-center py-20 text-gray-500 w-full aspect-video">
                <PlaySquare className="h-10 w-10 mb-2 opacity-50" />
                <p>Video is not ready yet.</p>
              </div>
            )}
          </div>

          {/* Bottom: Script Scenes */}
          <div className="flex-1 overflow-y-auto p-4 md:p-6 bg-white dark:bg-card">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Script & Scenes
            </h3>
            
            {loadingScenes ? (
              <div className="flex items-center justify-center py-10">
                <Loader2 className="h-6 w-6 animate-spin text-[#F875AA]" />
              </div>
            ) : error ? (
              <div className="text-red-500 text-sm p-4 bg-red-50 dark:bg-red-950/20 rounded-lg">{error}</div>
            ) : scenes.length === 0 ? (
              <div className="text-gray-500 text-sm italic">No scenes available for this video.</div>
            ) : (
              <div className="space-y-6">
                {scenes.map((scene, index) => (
                  <div key={scene.id} className="bg-gray-50 dark:bg-muted/30 p-4 rounded-xl border border-gray-100 dark:border-border/50">
                    <div className="text-xs font-bold text-[#F875AA] mb-3">SCENE {index + 1}</div>
                    
                    {scene.narration_script && (
                      <div className="mb-4">
                        <div className="text-xs font-semibold text-gray-500 dark:text-muted-foreground mb-1 uppercase">Narration</div>
                        <p className="text-gray-800 dark:text-foreground text-sm italic border-l-2 border-[#F875AA] pl-3 py-1">
                          &quot;{scene.narration_script}&quot;
                        </p>
                      </div>
                    )}
                    
                    {scene.visual_plan && (
                      <div>
                        <div className="text-xs font-semibold text-gray-500 dark:text-muted-foreground mb-1 uppercase">Visuals</div>
                        <div className="text-gray-700 dark:text-gray-300 text-sm bg-white dark:bg-card p-3 rounded border border-gray-100 dark:border-border">
                          {scene.visual_plan}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column (Chatbox) */}
        <div className="flex flex-col w-full lg:w-1/3 bg-white dark:bg-card h-[50vh] lg:h-full shrink-0">
          <div className="p-4 border-b border-gray-200 dark:border-border flex items-center gap-2 shrink-0">
            <MessageSquare className="h-4 w-4 text-[#F875AA]" />
            <h3 className="font-semibold text-gray-900 dark:text-foreground text-sm">Ask Questions</h3>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center py-10">
                <div className="mx-auto w-12 h-12 bg-pink-100 dark:bg-pink-950 rounded-full flex items-center justify-center mb-3">
                  <MessageSquare className="h-5 w-5 text-[#F875AA]" />
                </div>
                <p className="text-sm text-gray-500 dark:text-muted-foreground max-w-[200px] mx-auto">
                  Ask me anything about the video topic or the provided materials!
                </p>
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex flex-col max-w-[85%] ${
                  msg.role === "user" ? "ml-auto" : "mr-auto"
                }`}
              >
                <div
                  className={`p-3 rounded-2xl text-sm ${
                    msg.role === "user"
                      ? "bg-[#F875AA] text-white rounded-tr-sm"
                      : "bg-gray-100 dark:bg-muted text-gray-800 dark:text-foreground rounded-tl-sm"
                  }`}
                >
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}
            
            {isSending && (
              <div className="flex flex-col max-w-[85%] mr-auto">
                <div className="p-3 rounded-2xl rounded-tl-sm bg-gray-100 dark:bg-muted text-gray-800 dark:text-foreground text-sm flex items-center gap-2">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  Thinking...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-3 bg-white dark:bg-card border-t border-gray-200 dark:border-border shrink-0">
            <form onSubmit={handleSendMessage} className="flex items-end gap-2 relative">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask a question..."
                className="w-full resize-none min-h-[44px] max-h-32 p-3 pr-12 rounded-xl border border-gray-200 dark:border-border bg-gray-50 dark:bg-muted/50 focus:outline-none focus:ring-2 focus:ring-[#F875AA]/20 focus:border-[#F875AA]/30 text-sm transition-all"
                rows={1}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage(e);
                  }
                }}
              />
              <Button 
                type="submit" 
                size="icon" 
                disabled={!inputMessage.trim() || isSending}
                className="absolute right-1.5 bottom-1.5 h-8 w-8 rounded-lg bg-[#F875AA] hover:bg-[#e8609a] text-white transition-all disabled:opacity-50"
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
