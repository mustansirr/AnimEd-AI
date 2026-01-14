import Link from "next/link";
import { Button } from "@/components/ui/button";
import { PlusCircle, Library, Mic, Settings, LayoutDashboard } from "lucide-react";
import { cn } from "@/lib/utils";

export function Sidebar({ className }: { className?: string }) {
  return (
    <div className={cn("pb-12 w-64 border-r bg-gray-50/50 min-h-screen hidden md:block", className)}>
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-xl font-bold tracking-tight text-primary">
            AnimEd AI
          </h2>
          <div className="space-y-1 mt-4">
             <Button className="w-full justify-start gap-2 shadow-sm">
              <PlusCircle className="h-4 w-4" />
              New Project
            </Button>
          </div>
        </div>
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-xs font-semibold tracking-tight uppercase text-gray-500">
            Menu
          </h2>
          <div className="space-y-1">
            <Button variant="secondary" className="w-full justify-start">
              <LayoutDashboard className="mr-2 h-4 w-4" />
              Dashboard
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Library className="mr-2 h-4 w-4" />
              Library
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Mic className="mr-2 h-4 w-4" />
              Voices
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
