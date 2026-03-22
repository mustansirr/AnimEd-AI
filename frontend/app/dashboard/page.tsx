import { redirect } from "next/navigation";
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
      <div className="flex min-h-screen bg-gray-50 font-sans text-gray-900">
        {/* Sidebar - Fixed Left */}
        <Sidebar className="hidden md:block w-64 flex-shrink-0" />
        
        <div className="flex-1 flex flex-col min-w-0 h-screen">
          {/* Header - Fixed Top */}
          <Header />

          <main className="flex-1 overflow-y-auto px-4 md:px-6 py-12">
            <div className="flex flex-col items-center justify-start min-h-full">
              {/* Hero Heading */}
              <div className="text-center mb-8 mt-12">
                <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-3">
                  What&apos;s today&apos;s lesson or concept?
                </h1>
                <p className="text-gray-500 text-sm md:text-base max-w-lg mx-auto">
                  Transform complex topics into engaging AI-driven educational animations in seconds.
                </p>
              </div>

              {/* Centered Prompt Input */}
              <PromptInput />

              {/* Generation Pipeline (appears after Generate is clicked) */}
              <GenerationPipeline />
            </div>
          </main>
        </div>
      </div>
    </DashboardWrapper>
  );
}
