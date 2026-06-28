"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sparkles } from "lucide-react";

interface CreateFlashcardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onManualCreate: (front: string, back: string) => Promise<void>;
  onAIGenerate: (topic: string, count: number) => Promise<void>;
}

export function CreateFlashcardModal({ isOpen, onClose, onManualCreate, onAIGenerate }: CreateFlashcardModalProps) {
  const [activeTab, setActiveTab] = useState("manual");
  
  // Manual state
  const [front, setFront] = useState("");
  const [back, setBack] = useState("");
  
  // AI state
  const [topic, setTopic] = useState("");
  const [count, setCount] = useState(5);
  
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleManualSubmit = async () => {
    if (!front.trim() || !back.trim()) return;
    setIsSubmitting(true);
    try {
      await onManualCreate(front, back);
      setFront("");
      setBack("");
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAISubmit = async () => {
    if (!topic.trim()) return;
    setIsSubmitting(true);
    try {
      await onAIGenerate(topic, count);
      setTopic("");
      setCount(5);
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[500px] bg-white dark:bg-card border-gray-200 dark:border-border">
        <DialogHeader>
          <DialogTitle className="text-gray-900 dark:text-foreground">Add Flashcards</DialogTitle>
        </DialogHeader>
        
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full mt-2">
          <TabsList className="grid w-full grid-cols-2 mb-4 bg-gray-100 dark:bg-muted">
            <TabsTrigger value="manual" className="data-[state=active]:bg-white dark:data-[state=active]:bg-card dark:text-foreground">Manual</TabsTrigger>
            <TabsTrigger value="ai" className="data-[state=active]:bg-white dark:data-[state=active]:bg-card dark:text-foreground flex items-center gap-2">
              <Sparkles className="w-3 h-3 text-[#e8609a]" />
              Generate with AI
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="manual">
            <div className="grid gap-4 py-2">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-900 dark:text-foreground">Front (Question / Concept)</label>
                <Textarea 
                  value={front} 
                  onChange={(e) => setFront(e.target.value)} 
                  placeholder="e.g. What is the powerhouse of the cell?"
                  className="bg-white dark:bg-background border-gray-300 dark:border-border dark:text-foreground resize-none h-20"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-900 dark:text-foreground">Back (Answer)</label>
                <Textarea 
                  value={back} 
                  onChange={(e) => setBack(e.target.value)} 
                  placeholder="e.g. Mitochondria"
                  className="bg-white dark:bg-background border-gray-300 dark:border-border dark:text-foreground resize-none h-24"
                />
              </div>
            </div>
            <DialogFooter className="mt-4">
              <Button variant="outline" onClick={onClose} disabled={isSubmitting} className="border-gray-300 dark:border-border text-gray-700 dark:text-foreground hover:bg-gray-100 dark:hover:bg-muted">
                Cancel
              </Button>
              <Button onClick={handleManualSubmit} disabled={isSubmitting || !front.trim() || !back.trim()} className="bg-[#e8609a] hover:bg-[#d64a85] text-white">
                {isSubmitting ? "Saving..." : "Add Card"}
              </Button>
            </DialogFooter>
          </TabsContent>
          
          <TabsContent value="ai">
            <div className="grid gap-4 py-2">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-900 dark:text-foreground">Topic</label>
                <Textarea 
                  value={topic} 
                  onChange={(e) => setTopic(e.target.value)} 
                  placeholder="e.g. Fundamentals of Quantum Mechanics or paste a paragraph of text."
                  className="bg-white dark:bg-background border-gray-300 dark:border-border dark:text-foreground resize-none h-32"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-900 dark:text-foreground">Number of Cards</label>
                <Input 
                  type="number"
                  min={1}
                  max={20}
                  value={count} 
                  onChange={(e) => setCount(parseInt(e.target.value) || 5)} 
                  className="bg-white dark:bg-background border-gray-300 dark:border-border dark:text-foreground"
                />
                <p className="text-xs text-gray-500 dark:text-muted-foreground">Max 20 cards per generation.</p>
              </div>
            </div>
            <DialogFooter className="mt-4">
              <Button variant="outline" onClick={onClose} disabled={isSubmitting} className="border-gray-300 dark:border-border text-gray-700 dark:text-foreground hover:bg-gray-100 dark:hover:bg-muted">
                Cancel
              </Button>
              <Button onClick={handleAISubmit} disabled={isSubmitting || !topic.trim()} className="bg-[#e8609a] hover:bg-[#d64a85] text-white flex items-center gap-2">
                {isSubmitting ? (
                  "Generating..."
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Generate
                  </>
                )}
              </Button>
            </DialogFooter>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
