"use client";

import { useEffect, useState } from "react";
import { Plus, Clock, Target, Trash2 } from "lucide-react";
import { getQuizzes, deleteQuiz, Quiz } from "@/lib/api";
import { createClient } from "@/utils/supabase/client";
import { Button } from "@/components/ui/button";
import { DashboardWrapper } from "@/components/dashboard/DashboardWrapper";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { formatDistanceToNow } from "date-fns";
import { CreateQuizModal } from "@/components/quizzes/CreateQuizModal";
import Link from "next/link";
import { toast } from "sonner";

export default function QuizzesPage() {
  const [userId, setUserId] = useState<string | null>(null);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const fetchQuizzes = async (uid: string) => {
    if (!uid) return;
    try {
      setIsLoading(true);
      const data = await getQuizzes(uid);
      setQuizzes(data);
    } catch (error) {
      console.error("Failed to fetch quizzes", error);
      toast.error("Failed to load quizzes");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const init = async () => {
      const supabase = createClient();
      const { data: { user: supabaseUser } } = await supabase.auth.getUser();
      if (supabaseUser) {
        setUserId(supabaseUser.id);
        fetchQuizzes(supabaseUser.id);
      } else {
        setIsLoading(false);
      }
    };
    init();
  }, []);

  const handleDelete = async (quizId: string, e: React.MouseEvent) => {
    e.preventDefault(); // prevent navigation
    if (!userId) return;
    try {
      await deleteQuiz(userId, quizId);
      toast.success("Quiz deleted");
      fetchQuizzes(userId);
    } catch (error) {
      console.error(error);
      toast.error("Failed to delete quiz");
    }
  };

  return (
    <DashboardWrapper>
      <div className="flex min-h-screen bg-[#FFF6F6] dark:bg-background font-sans text-gray-900 dark:text-foreground relative transition-colors">
        <div className="fixed inset-0 z-0 bg-[linear-gradient(to_right,#FFDFDF_1px,transparent_1px),linear-gradient(to_bottom,#FFDFDF_1px,transparent_1px)] dark:bg-[linear-gradient(to_right,rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

        <Sidebar className="hidden md:block w-64 flex-shrink-0 z-10" />
        
        <div className="flex-1 flex flex-col min-w-0 h-screen z-10 relative">
          <Header />

          <main className="flex-1 overflow-y-auto px-4 md:px-8 py-8">
            <div className="max-w-6xl mx-auto">
              <div className="flex justify-between items-center mb-8">
                <div>
                  <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-foreground">Quizzes & Tests</h1>
                  <p className="text-slate-500 dark:text-muted-foreground mt-2">Test your knowledge with AI-generated quizzes.</p>
                </div>
                <Button onClick={() => setIsCreateModalOpen(true)} className="bg-pink-500 hover:bg-pink-600 text-white">
                  <Plus className="mr-2 h-4 w-4" /> Generate Quiz
                </Button>
              </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-40 rounded-xl border border-slate-200 dark:border-border bg-slate-100 dark:bg-muted/50 animate-pulse" />
          ))}
        </div>
      ) : quizzes.length === 0 ? (
        <div className="text-center py-20 border border-dashed rounded-xl border-slate-300 dark:border-border">
          <Target className="mx-auto h-12 w-12 text-slate-400 mb-4" />
          <h2 className="text-xl font-semibold mb-2 text-slate-900 dark:text-foreground">No quizzes yet</h2>
          <p className="text-slate-500 mb-6 max-w-sm mx-auto">Generate your first AI quiz to start testing your knowledge.</p>
          <Button onClick={() => setIsCreateModalOpen(true)} className="bg-pink-500 hover:bg-pink-600 text-white">
            <Plus className="mr-2 h-4 w-4" /> Create First Quiz
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {quizzes.map((quiz) => (
            <Link key={quiz.id} href={`/quizzes/${quiz.id}`}>
              <div className="group relative rounded-xl border border-slate-200 dark:border-border bg-white dark:bg-card p-6 shadow-sm hover:shadow-md transition-all cursor-pointer h-full flex flex-col hover:border-pink-500/50">
                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10"
                    onClick={(e) => handleDelete(quiz.id, e)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>

                <div className="flex-1">
                  <div className="mb-2 pr-8">
                    <h3 className="font-semibold text-lg text-slate-900 dark:text-foreground group-hover:text-pink-500 transition-colors line-clamp-1 mb-2">
                      {quiz.title}
                    </h3>
                    {quiz.difficulty && (
                      <span className={`inline-block text-xs px-2 py-0.5 rounded-full border font-medium uppercase tracking-wider ${
                        quiz.difficulty.toLowerCase() === 'easy' ? 'bg-green-50 text-green-700 border-green-200 dark:bg-green-500/10 dark:text-green-400 dark:border-green-500/20' :
                        quiz.difficulty.toLowerCase() === 'hard' ? 'bg-red-50 text-red-700 border-red-200 dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/20' :
                        'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/20'
                      }`}>
                        {quiz.difficulty}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center text-sm text-slate-500 dark:text-muted-foreground mt-4 space-x-4">
                    <span className="flex items-center">
                      <Target className="mr-1.5 h-4 w-4" />
                      {quiz.total_questions} Questions
                    </span>
                    <span className="flex items-center">
                      <Clock className="mr-1.5 h-4 w-4" />
                      {formatDistanceToNow(new Date(quiz.created_at), { addSuffix: true })}
                    </span>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-100 dark:border-border flex justify-between items-center">
                  {quiz.score !== null && quiz.score !== undefined ? (
                    <div className="flex flex-col">
                      <span className="text-xs text-slate-500 dark:text-muted-foreground uppercase font-medium tracking-wider">Score</span>
                      <span className="font-semibold text-slate-900 dark:text-foreground">
                        {quiz.score} / {quiz.total_questions} ({(quiz.score / quiz.total_questions * 100).toFixed(0)}%)
                      </span>
                    </div>
                  ) : (
                    <div className="flex flex-col">
                      <span className="text-xs text-slate-500 dark:text-muted-foreground uppercase font-medium tracking-wider">Status</span>
                      <span className="font-medium text-amber-500">Not Started</span>
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

              <CreateQuizModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onQuizCreated={() => userId && fetchQuizzes(userId)}
              />
            </div>
          </main>
        </div>
      </div>
    </DashboardWrapper>
  );
}
