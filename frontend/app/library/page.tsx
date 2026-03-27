import { redirect } from "next/navigation";
import { createClient } from "@/utils/supabase/server";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { VideoGrid } from "@/components/dashboard/VideoGrid";
import { DashboardWrapper } from "@/components/dashboard/DashboardWrapper";

export default async function LibraryPage() {
  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return redirect("/");
  }

  return (
    <DashboardWrapper>
      <div className="flex min-h-screen bg-[#FFF6F6] font-sans text-gray-900 relative selection:bg-[#FFDFDF] selection:text-[#e8609a]">
        <div className="fixed inset-0 z-0 bg-[linear-gradient(to_right,#FFDFDF_1px,transparent_1px),linear-gradient(to_bottom,#FFDFDF_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

        {/* Sidebar - Fixed Left */}
        <Sidebar className="hidden md:block w-64 flex-shrink-0 z-10" />

        <div className="flex-1 flex flex-col min-w-0 h-screen z-10 relative">
          {/* Header - Fixed Top */}
          <Header />

          <main className="flex-1 overflow-auto p-4 md:p-6">
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900">My Library</h1>
              <p className="text-sm text-gray-500 mt-1">
                View, play, and manage your generated videos
              </p>
            </div>

            <VideoGrid />
          </main>
        </div>
      </div>
    </DashboardWrapper>
  );
}
