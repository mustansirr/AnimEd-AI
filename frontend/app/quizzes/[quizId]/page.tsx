"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getQuizById, submitQuiz, retakeQuiz, Quiz } from "@/lib/api";
import { createClient } from "@/utils/supabase/client";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { ArrowLeft, ArrowRight, CheckCircle2, XCircle, ChevronLeft, RefreshCcw } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { DashboardWrapper } from "@/components/dashboard/DashboardWrapper";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";

export default function QuizSessionPage() {
  const [userId, setUserId] = useState<string | null>(null);
  const params = useParams();
  const router = useRouter();
  const quizId = params.quizId as string;

  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // State for the active session
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<string, number>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRetaking, setIsRetaking] = useState(false);

  useEffect(() => {
    const fetchQuiz = async () => {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        setIsLoading(false);
        return;
      }
      setUserId(user.id);

      try {
        const data = await getQuizById(user.id, quizId);
        setQuiz(data);
        
        // If it was already submitted before, prepopulate answers
        if (data.score !== null && data.score !== undefined && data.questions) {
          const pastAnswers: Record<string, number> = {};
          data.questions.forEach((q) => {
            if (q.user_answer_index !== null && q.user_answer_index !== undefined) {
              pastAnswers[q.id] = q.user_answer_index;
            }
          });
          setUserAnswers(pastAnswers);
        }
      } catch (error) {
        console.error(error);
        toast.error("Failed to load quiz");
      } finally {
        setIsLoading(false);
      }
    };
    fetchQuiz();
  }, [quizId]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-500"></div>
      </div>
    );
  }

  if (!quiz || !quiz.questions || quiz.questions.length === 0) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-foreground">Quiz not found</h2>
        <p className="text-slate-500 mt-2">The quiz you are looking for does not exist.</p>
        <Button onClick={() => router.push("/quizzes")} className="mt-4">Back to Quizzes</Button>
      </div>
    );
  }

  const isCompleted = quiz.score !== null && quiz.score !== undefined;
  const currentQuestion = quiz.questions[currentIndex];
  
  const handleSelectOption = (optionIndex: number) => {
    if (isCompleted) return; // Don't allow changing answers if already submitted
    setUserAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: optionIndex
    }));
  };

  const handleSubmit = async () => {
    if (!userId) return;
    
    // Check if all answered
    if (Object.keys(userAnswers).length < quiz.questions!.length) {
      const confirm = window.confirm("You haven't answered all questions. Are you sure you want to submit?");
      if (!confirm) return;
    }

    try {
      setIsSubmitting(true);
      const updatedQuiz = await submitQuiz(userId, quizId, userAnswers);
      setQuiz(updatedQuiz);
      toast.success("Quiz submitted successfully!");
      window.scrollTo(0, 0); // Scroll to top for results
    } catch (error) {
      console.error(error);
      toast.error("Failed to submit quiz");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetake = async () => {
    if (!userId) return;
    try {
      setIsRetaking(true);
      const resetQuiz = await retakeQuiz(userId, quizId);
      setQuiz(resetQuiz);
      setUserAnswers({});
      setCurrentIndex(0);
      toast.success("Quiz reset. Good luck!");
    } catch (error) {
      console.error(error);
      toast.error("Failed to retake quiz");
    } finally {
      setIsRetaking(false);
    }
  };

  // --- RENDER COMPLETED STATE ---
  if (isCompleted) {
    const percentage = Math.round((quiz.score! / quiz.total_questions) * 100);
    return (
      <DashboardWrapper>
        <div className="flex min-h-screen bg-[#FFF6F6] dark:bg-background font-sans text-gray-900 dark:text-foreground relative transition-colors">
          <div className="fixed inset-0 z-0 bg-[linear-gradient(to_right,#FFDFDF_1px,transparent_1px),linear-gradient(to_bottom,#FFDFDF_1px,transparent_1px)] dark:bg-[linear-gradient(to_right,rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

          <Sidebar className="hidden md:block w-64 flex-shrink-0 z-10" />
          
          <div className="flex-1 flex flex-col min-w-0 h-screen z-10 relative">
            <Header />

            <main className="flex-1 overflow-y-auto px-4 md:px-8 py-8">
              <div className="container mx-auto max-w-4xl">
                <Link href="/quizzes" className="inline-flex items-center text-slate-500 hover:text-slate-900 dark:hover:text-foreground mb-8">
                  <ChevronLeft className="mr-1 h-4 w-4" /> Back to Quizzes
                </Link>
                
                <div className="bg-white dark:bg-card border border-slate-200 dark:border-border rounded-2xl p-8 mb-8 text-center shadow-sm">
                  <h1 className="text-3xl font-bold mb-2 text-slate-900 dark:text-foreground">{quiz.title}</h1>
                  <p className="text-slate-500 dark:text-muted-foreground mb-6">You scored {quiz.score} out of {quiz.total_questions}</p>
                  
                  <div className="inline-flex items-center justify-center w-32 h-32 rounded-full border-8 border-slate-100 dark:border-muted relative">
                    <svg className="absolute inset-0 w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                      <circle
                        className={percentage >= 70 ? "text-green-500" : percentage >= 40 ? "text-amber-500" : "text-red-500"}
                        strokeWidth="8"
                        strokeDasharray={`${percentage * 2.83} 283`}
                        strokeLinecap="round"
                        stroke="currentColor"
                        fill="transparent"
                        r="45"
                        cx="50"
                        cy="50"
                      />
                    </svg>
                    <span className="text-3xl font-bold text-slate-900 dark:text-foreground">{percentage}%</span>
                  </div>
                  <div className="mt-8">
                    <Button onClick={handleRetake} disabled={isRetaking} className="bg-pink-500 hover:bg-pink-600 text-white">
                      <RefreshCcw className={`mr-2 h-4 w-4 ${isRetaking ? 'animate-spin' : ''}`} />
                      Retake Quiz
                    </Button>
                  </div>
                </div>

        <div className="space-y-6">
          <h2 className="text-xl font-bold text-slate-900 dark:text-foreground mb-4">Detailed Review</h2>
          {quiz.questions.map((q, idx) => {
            const isCorrect = q.user_answer_index === q.correct_option_index;
            return (
              <div key={q.id} className={cn(
                "p-6 rounded-xl border shadow-sm",
                isCorrect ? "border-green-200 bg-green-50/50 dark:bg-green-500/5 dark:border-green-500/20" : "border-red-200 bg-red-50/50 dark:bg-red-500/5 dark:border-red-500/20"
              )}>
                <div className="flex items-start gap-4 mb-4">
                  {isCorrect ? (
                    <CheckCircle2 className="h-6 w-6 text-green-500 mt-0.5 shrink-0" />
                  ) : (
                    <XCircle className="h-6 w-6 text-red-500 mt-0.5 shrink-0" />
                  )}
                  <div>
                    <h3 className="text-lg font-medium text-slate-900 dark:text-foreground mb-1">
                      {idx + 1}. {q.question_text}
                    </h3>
                  </div>
                </div>
                
                <div className="space-y-2 ml-10 mb-4">
                  {q.options.map((opt, optIdx) => {
                    const isSelected = q.user_answer_index === optIdx;
                    const isActualCorrect = q.correct_option_index === optIdx;
                    
                    let optionStyle = "border-slate-200 dark:border-border bg-white dark:bg-card text-slate-700 dark:text-slate-300";
                    if (isActualCorrect) {
                      optionStyle = "border-green-500 bg-green-50 dark:bg-green-500/10 text-green-700 dark:text-green-400 font-medium";
                    } else if (isSelected && !isActualCorrect) {
                      optionStyle = "border-red-500 bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400";
                    }

                    return (
                      <div key={optIdx} className={cn("p-3 rounded-lg border text-sm", optionStyle)}>
                        <div className="flex justify-between items-center">
                          <span>{opt}</span>
                          {isSelected && <span className="text-xs uppercase tracking-wider opacity-70">Your Answer</span>}
                          {isActualCorrect && !isSelected && <span className="text-xs uppercase tracking-wider opacity-70">Correct Answer</span>}
                        </div>
                      </div>
                    );
                  })}
                </div>

                {q.explanation && (
                  <div className="ml-10 mt-4 p-4 rounded-lg bg-slate-50 dark:bg-black/20 text-sm text-slate-600 dark:text-slate-400 italic">
                    <span className="font-semibold not-italic mr-2">Explanation:</span>
                    {q.explanation}
                  </div>
                )}
              </div>
            );
          })}
        </div>
              </div>
            </main>
          </div>
        </div>
      </DashboardWrapper>
    );
  }

  // --- RENDER ACTIVE SESSION STATE ---
  const progressPercentage = ((currentIndex + 1) / quiz.total_questions) * 100;

  return (
    <DashboardWrapper>
      <div className="flex min-h-screen bg-[#FFF6F6] dark:bg-background font-sans text-gray-900 dark:text-foreground relative transition-colors">
        <div className="fixed inset-0 z-0 bg-[linear-gradient(to_right,#FFDFDF_1px,transparent_1px),linear-gradient(to_bottom,#FFDFDF_1px,transparent_1px)] dark:bg-[linear-gradient(to_right,rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

        <Sidebar className="hidden md:block w-64 flex-shrink-0 z-10" />
        
        <div className="flex-1 flex flex-col min-w-0 h-screen z-10 relative">
          <Header />

          <main className="flex-1 overflow-y-auto px-4 md:px-8 py-8">
            <div className="container mx-auto max-w-3xl">
              <Link href="/quizzes" className="inline-flex items-center text-slate-500 hover:text-slate-900 dark:hover:text-foreground mb-6">
                <ChevronLeft className="mr-1 h-4 w-4" /> Save & Exit
              </Link>
        
        {/* Progress Bar */}
        <div className="mb-12">
          <div className="flex justify-between text-sm font-medium text-slate-500 mb-2">
            <span>Question {currentIndex + 1} of {quiz.total_questions}</span>
            <span>{Math.round(progressPercentage)}%</span>
          </div>
          <div className="h-2 w-full bg-slate-200 dark:bg-muted rounded-full overflow-hidden">
            <div 
              className="h-full bg-pink-500 transition-all duration-300 ease-in-out rounded-full"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white/80 dark:bg-card/80 backdrop-blur-xl border border-slate-200 dark:border-border rounded-3xl p-8 md:p-12 shadow-sm min-h-[400px] flex flex-col relative overflow-hidden">
          {/* Subtle decorative glow */}
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-pink-500/10 rounded-full blur-3xl pointer-events-none" />
          
          <h2 className="text-2xl md:text-3xl font-semibold text-slate-900 dark:text-foreground mb-10 leading-tight">
            {currentQuestion.question_text}
          </h2>

          <div className="space-y-4 flex-1">
            {currentQuestion.options.map((option, idx) => {
              const isSelected = userAnswers[currentQuestion.id] === idx;
              
              return (
                <button
                  key={idx}
                  onClick={() => handleSelectOption(idx)}
                  className={cn(
                    "w-full text-left p-5 rounded-2xl border transition-all duration-200 text-lg",
                    isSelected 
                      ? "border-pink-500 bg-pink-50 dark:bg-pink-500/10 text-pink-700 dark:text-pink-300 shadow-sm"
                      : "border-slate-200 dark:border-border bg-white dark:bg-card/50 text-slate-700 dark:text-slate-300 hover:border-pink-300 hover:bg-slate-50 dark:hover:bg-muted"
                  )}
                >
                  <div className="flex items-center">
                    <div className={cn(
                      "flex items-center justify-center w-8 h-8 rounded-full border mr-4 shrink-0 transition-colors",
                      isSelected
                        ? "border-pink-500 bg-pink-500 text-white"
                        : "border-slate-300 dark:border-slate-600 text-slate-500"
                    )}>
                      {String.fromCharCode(65 + idx)}
                    </div>
                    {option}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-8 flex justify-between items-center">
          <Button
            variant="outline"
            size="lg"
            onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
            disabled={currentIndex === 0}
            className="rounded-xl px-6"
          >
            <ArrowLeft className="mr-2 h-4 w-4" /> Previous
          </Button>

          {currentIndex === quiz.total_questions - 1 ? (
            <Button
              size="lg"
              onClick={handleSubmit}
              disabled={isSubmitting || Object.keys(userAnswers).length < quiz.total_questions}
              className="rounded-xl px-8 bg-pink-500 hover:bg-pink-600 text-white shadow-md shadow-pink-500/20"
            >
              {isSubmitting ? "Submitting..." : "Submit Quiz"}
            </Button>
          ) : (
            <Button
              size="lg"
              onClick={() => setCurrentIndex((prev) => Math.min(quiz.total_questions - 1, prev + 1))}
              className="rounded-xl px-8"
              disabled={userAnswers[currentQuestion.id] === undefined} // Disable next if not answered
            >
              Next <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          )}
            </div>
          </div>
        </main>
      </div>
    </div>
    </DashboardWrapper>
  );
}
