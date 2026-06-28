"use client";

import { useState, useEffect } from "react";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Flashcard } from "@/lib/api";
import { cn } from "@/lib/utils";

interface FlashcardStudyModalProps {
  isOpen: boolean;
  onClose: () => void;
  cards: Flashcard[];
  onReview: (cardId: string, rating: number) => Promise<void>;
}

export function FlashcardStudyModal({ isOpen, onClose, cards, onReview }: FlashcardStudyModalProps) {
  const [studyQueue, setStudyQueue] = useState<Flashcard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    if (isOpen && !isInitialized) {
      // Prioritize due cards first
      const sortedCards = [...cards].sort((a, b) => {
        const aDue = new Date(a.next_review_date) <= new Date();
        const bDue = new Date(b.next_review_date) <= new Date();
        if (aDue && !bDue) return -1;
        if (!aDue && bDue) return 1;
        return 0;
      });
      setStudyQueue(sortedCards);
      setCurrentIndex(0);
      setShowAnswer(false);
      setIsInitialized(true);
    } else if (!isOpen) {
      setIsInitialized(false);
    }
  }, [isOpen, cards, isInitialized]);

  const currentCard = studyQueue[currentIndex];

  const handleReview = async (rating: number) => {
    if (!currentCard) return;
    setIsSubmitting(true);
    try {
      await onReview(currentCard.id, rating);
      setShowAnswer(false);
      
      if (rating === 1 || rating === 2) {
        // Again or Hard -> push to the end of the queue
        setStudyQueue(prev => [...prev, currentCard]);
      }
      
      setCurrentIndex(prev => prev + 1);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setCurrentIndex(0);
    setShowAnswer(false);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent className="sm:max-w-[600px] p-0 bg-transparent border-none shadow-none">
        
        {currentIndex >= studyQueue.length ? (
          <div className="bg-white dark:bg-card rounded-xl p-12 text-center border border-gray-200 dark:border-border">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-foreground mb-4">🎉 You&apos;re all caught up!</h2>
            <p className="text-gray-500 dark:text-muted-foreground mb-8">You have reviewed all cards in this session.</p>
            <Button onClick={handleClose} className="bg-[#e8609a] hover:bg-[#d64a85] text-white">
              Back to Deck
            </Button>
          </div>
        ) : (
          <div className="flex flex-col gap-6">
            <div className="text-center text-white font-medium bg-black/40 backdrop-blur-md py-1 px-4 rounded-full self-center">
              Card {currentIndex + 1} of {studyQueue.length}
            </div>

            <div className="w-full [perspective:1000px]">
              <div 
                className={cn(
                  "w-full min-h-[300px] relative [transform-style:preserve-3d] transition-transform duration-500 cursor-pointer",
                  showAnswer ? "[transform:rotateY(180deg)]" : ""
                )}
                onClick={() => setShowAnswer(!showAnswer)}
              >
                {/* Front of card */}
                <div className="absolute inset-0 [backface-visibility:hidden] bg-white dark:bg-card rounded-2xl p-8 flex items-center justify-center text-center shadow-xl border border-gray-200 dark:border-border">
                  <h3 className="text-2xl md:text-3xl font-medium text-gray-900 dark:text-foreground leading-relaxed">
                    {currentCard?.front}
                  </h3>
                  <div className="absolute bottom-4 left-0 right-0 text-center text-sm text-gray-400 dark:text-muted-foreground animate-pulse">
                    Click to show answer
                  </div>
                </div>

                {/* Back of card */}
                <div className="absolute inset-0 [backface-visibility:hidden] [transform:rotateY(180deg)] bg-white dark:bg-card rounded-2xl p-8 flex flex-col items-center justify-center text-center shadow-xl border border-gray-200 dark:border-border overflow-y-auto">
                  <div className="text-sm font-semibold text-[#e8609a] mb-4 uppercase tracking-wider">Answer</div>
                  <div className="text-xl text-gray-900 dark:text-foreground leading-relaxed">
                    {currentCard?.back}
                  </div>
                </div>
              </div>
            </div>

            {showAnswer && (
              <div className="bg-white dark:bg-card rounded-xl p-4 shadow-xl border border-gray-200 dark:border-border flex gap-2 justify-center animate-in fade-in slide-in-from-bottom-4">
                <Button 
                  onClick={() => handleReview(1)} 
                  disabled={isSubmitting}
                  className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 dark:bg-red-900/30 dark:hover:bg-red-900/50 dark:text-red-400"
                >
                  Again <span className="text-xs ml-1 opacity-70">(&lt;1m)</span>
                </Button>
                <Button 
                  onClick={() => handleReview(2)} 
                  disabled={isSubmitting}
                  className="flex-1 bg-orange-100 hover:bg-orange-200 text-orange-700 dark:bg-orange-900/30 dark:hover:bg-orange-900/50 dark:text-orange-400"
                >
                  Hard
                </Button>
                <Button 
                  onClick={() => handleReview(3)} 
                  disabled={isSubmitting}
                  className="flex-1 bg-green-100 hover:bg-green-200 text-green-700 dark:bg-green-900/30 dark:hover:bg-green-900/50 dark:text-green-400"
                >
                  Good
                </Button>
                <Button 
                  onClick={() => handleReview(4)} 
                  disabled={isSubmitting}
                  className="flex-1 bg-blue-100 hover:bg-blue-200 text-blue-700 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 dark:text-blue-400"
                >
                  Easy
                </Button>
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
