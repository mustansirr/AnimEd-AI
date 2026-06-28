import { redirect } from "next/navigation";
import Link from "next/link";
import { Brain, ArrowRight } from "lucide-react";
import { createClient } from "@/utils/supabase/server";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { PromptInput } from "@/components/dashboard/PromptInput";
import { GenerationPipeline } from "@/components/dashboard/GenerationPipeline";
import { DashboardWrapper } from "@/components/dashboard/DashboardWrapper";

export default async function DashboardPage() {
  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return redirect("/");
  }

  return (
    <DashboardWrapper>
      <div className="flex min-h-screen bg-[#FFF6F6] dark:bg-background font-sans text-gray-900 dark:text-foreground relative selection:bg-[#FFDFDF] dark:selection:bg-primary/20 selection:text-[#e8609a] dark:selection:text-primary transition-colors">
        <div className="fixed inset-0 z-0 bg-[linear-gradient(to_right,#FFDFDF_1px,transparent_1px),linear-gradient(to_bottom,#FFDFDF_1px,transparent_1px)] dark:bg-[linear-gradient(to_right,rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

        {/* Sidebar - Fixed Left */}
        <Sidebar className="hidden md:block w-64 flex-shrink-0 z-10" />
        
        <div className="flex-1 flex flex-col min-w-0 h-screen z-10 relative">
          {/* Header - Fixed Top */}
          <Header />

          <main className="flex-1 overflow-y-auto px-4 md:px-6 py-12">
            <div className="flex flex-col items-center justify-start min-h-full">
              {/* Hero Heading */}
              <div className="text-center mb-8 mt-12">
                <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-foreground mb-3">
                  What&apos;s today&apos;s lesson or concept?
                </h1>
              </div>

              {/* Centered Prompt Input */}
              <PromptInput />

              {/* Generation Pipeline (appears after Generate is clicked) */}
              <GenerationPipeline />

              {/* Flashcards Quick Link */}
              <div className="mt-12 w-full max-w-3xl mx-auto">
                <Link href="/flashcards">
                  <div className="bg-white dark:bg-card border border-gray-200 dark:border-border rounded-xl p-6 hover:shadow-md transition-shadow flex items-center justify-between cursor-pointer group">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-full bg-[#FFDFDF] dark:bg-primary/20 flex items-center justify-center">
                        <Brain className="h-6 w-6 text-[#e8609a] dark:text-primary" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-foreground">Study with Flashcards</h3>
                        <p className="text-sm text-gray-500 dark:text-muted-foreground">Review your AI-generated flashcards using spaced repetition.</p>
                      </div>
                    </div>
                    <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-[#e8609a] transition-colors" />
                  </div>
                </Link>
              </div>
            </div>
          </main>
        </div>
      </div>
    </DashboardWrapper>
  );
}
