import { redirect } from "next/navigation";
import { createClient } from "@/utils/supabase/server";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { PromptInput } from "@/components/dashboard/PromptInput";
import { Pipeline } from "@/components/dashboard/Pipeline";
import { VideoPlayer } from "@/components/dashboard/VideoPlayer";

export default async function DashboardPage() {
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

        <main className="flex-1 overflow-hidden p-4 md:p-6 flex flex-col gap-6">
            {/* Top Section: Prompt Input */}
            <div className="w-full flex-shrink-0">
                <PromptInput />
            </div>

            {/* Bottom Section: Split View (Video + Pipeline) */}
            <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-12 gap-6">
                
                {/* Left: Video Player */}
                <div className="lg:col-span-8 h-full flex flex-col min-h-0">
                     <div className="bg-white rounded-lg border shadow-sm p-4 h-full flex flex-col">
                        <div className="flex justify-between items-center mb-3">
                             <h3 className="font-semibold text-sm">Video Player</h3>
                             <span className="text-[10px] text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-100 flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                Rendering Preview
                             </span>
                        </div>
                        <div className="flex-1 min-h-0 bg-gray-900 rounded-md overflow-hidden relative">
                             <VideoPlayer />
                        </div>
                         {/* Player Controls / Scrubber (Placeholder) */}
                         <div className="h-8 mt-2 flex items-center px-2">
                             <div className="w-full h-1 bg-gray-100 rounded-full overflow-hidden">
                                 <div className="h-full w-1/3 bg-indigo-500 rounded-full" />
                             </div>
                         </div>
                     </div>
                </div>

                {/* Right: Pipeline */}
                <div className="lg:col-span-4 h-full min-h-0">
                    <Pipeline />
                </div>

            </div>
        </main>
      </div>
    </div>
  );
}
