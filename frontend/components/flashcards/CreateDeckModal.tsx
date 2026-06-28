"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

interface CreateDeckModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (title: string, description: string) => Promise<void>;
}

export function CreateDeckModal({ isOpen, onClose, onCreate }: CreateDeckModalProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!title.trim()) return;
    setIsSubmitting(true);
    try {
      await onCreate(title, description);
      setTitle("");
      setDescription("");
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[425px] bg-white dark:bg-card border-gray-200 dark:border-border">
        <DialogHeader>
          <DialogTitle className="text-gray-900 dark:text-foreground">Create New Deck</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-900 dark:text-foreground">Deck Title</label>
            <Input 
              value={title} 
              onChange={(e) => setTitle(e.target.value)} 
              placeholder="e.g. Introduction to Physics"
              className="bg-white dark:bg-background border-gray-300 dark:border-border dark:text-foreground"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-900 dark:text-foreground">Description (Optional)</label>
            <Textarea 
              value={description} 
              onChange={(e) => setDescription(e.target.value)} 
              placeholder="What are these flashcards about?"
              className="bg-white dark:bg-background border-gray-300 dark:border-border dark:text-foreground resize-none h-20"
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isSubmitting} className="border-gray-300 dark:border-border text-gray-700 dark:text-foreground hover:bg-gray-100 dark:hover:bg-muted">
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting || !title.trim()} className="bg-[#e8609a] hover:bg-[#d64a85] text-white">
            {isSubmitting ? "Creating..." : "Create Deck"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
