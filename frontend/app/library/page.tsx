import { redirect } from "next/navigation";
import { createClient } from "@/utils/supabase/server";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { VideoGrid } from "@/components/dashboard/VideoGrid";

export default async function LibraryPage() {
  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return redirect("/");
  }

  return (
    <div className="flex min-h-screen bg-gray-50 font-sans text-gray-900">
      {/* Sidebar - Fixed Left */}
      <Sidebar className="hidden md:block w-64 flex-shrink-0" />

      <div className="flex-1 flex flex-col min-w-0 h-screen">
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
  );
}
