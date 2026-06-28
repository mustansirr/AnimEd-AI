import { redirect } from "next/navigation";
import { createClient } from "@/utils/supabase/server";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { DashboardWrapper } from "@/components/dashboard/DashboardWrapper";
import { PomodoroTimer } from "@/components/pomodoro/PomodoroTimer";

export default async function PomodoroPage() {
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

          <main className="flex-1 overflow-auto p-4 md:p-6 lg:p-12">
            <div className="mb-10 text-center max-w-lg mx-auto">
              <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-foreground mb-2">
                Pomodoro Focus
              </h1>
              <p className="text-gray-500 dark:text-muted-foreground">
                Stay focused and track your study sessions with the Pomodoro technique.
              </p>
            </div>

            <PomodoroTimer />
          </main>
        </div>
      </div>
    </DashboardWrapper>
  );
}
