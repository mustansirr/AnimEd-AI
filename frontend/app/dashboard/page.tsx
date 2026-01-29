import { redirect } from "next/navigation";
import { createClient } from "@/utils/supabase/server";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { PromptInput } from "@/components/dashboard/PromptInput";
import { Pipeline } from "@/components/dashboard/Pipeline";
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

          <main className="flex-1 overflow-hidden p-4 md:p-6 flex flex-col gap-6">
              {/* Top Section: Prompt Input */}
              <div className="w-full flex-shrink-0">
                  <PromptInput />
              </div>

              {/* Bottom Section: Pipeline */}
              <div className="flex-1 min-h-0">
                  <Pipeline />
              </div>
          </main>
        </div>
      </div>
    </DashboardWrapper>
  );
}


