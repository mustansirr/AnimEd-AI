import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { generateQuiz } from "@/lib/api";
import { createClient } from "@/utils/supabase/client";
import { useEffect } from "react";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

interface CreateQuizModalProps {
  isOpen: boolean;
  onClose: () => void;
  onQuizCreated: () => void;
}

export function CreateQuizModal({ isOpen, onClose, onQuizCreated }: CreateQuizModalProps) {
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      if (user) setUserId(user.id);
    };
    fetchUser();
  }, []);
  const router = useRouter();
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("Medium");
  const [count, setCount] = useState(5);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    if (!userId) return;
    if (!topic.trim()) {
      toast.error("Please enter a topic");
      return;
    }

    try {
      setIsGenerating(true);
      const newQuiz = await generateQuiz(userId, topic, count, difficulty);
      toast.success("Quiz generated successfully!");
      setTopic("");
      setDifficulty("Medium");
      setCount(5);
      onQuizCreated();
      onClose();
      // Navigate straight to the quiz
      router.push(`/quizzes/${newQuiz.id}`);
    } catch (error) {
      console.error(error);
      toast.error("Failed to generate quiz. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && !isGenerating && onClose()}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Generate AI Quiz</DialogTitle>
          <DialogDescription>
            Enter a topic and our AI will generate a multiple-choice quiz for you.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="topic">Topic</Label>
            <Input
              id="topic"
              placeholder="e.g. History of Rome, Python Basics"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              disabled={isGenerating}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="count">Number of Questions</Label>
            <div className="flex items-center space-x-2">
              <Input
                id="count"
                type="number"
                min={1}
                max={20}
                value={count}
                onChange={(e) => setCount(parseInt(e.target.value) || 5)}
                disabled={isGenerating}
                className="w-24"
              />
              <span className="text-sm text-slate-500">Max 20</span>
            </div>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="difficulty">Difficulty</Label>
            <Select value={difficulty} onValueChange={setDifficulty} disabled={isGenerating}>
              <SelectTrigger id="difficulty">
                <SelectValue placeholder="Select difficulty" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Easy">Easy</SelectItem>
                <SelectItem value="Medium">Medium</SelectItem>
                <SelectItem value="Hard">Hard</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isGenerating}>
            Cancel
          </Button>
          <Button onClick={handleGenerate} disabled={isGenerating} className="bg-pink-500 hover:bg-pink-600 text-white">
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              "Generate"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
