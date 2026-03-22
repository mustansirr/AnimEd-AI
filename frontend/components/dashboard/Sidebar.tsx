"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Library, LayoutDashboard } from "lucide-react";
import { cn } from "@/lib/utils";

export function Sidebar({ className }: { className?: string }) {
  const pathname = usePathname();

  return (
    <div className={cn("pb-12 w-64 border-r bg-gray-50/50 min-h-screen hidden md:block", className)}>
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-xl font-bold tracking-tight text-primary">
            AnimEd AI
          </h2>
        </div>
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-xs font-semibold tracking-tight uppercase text-gray-500">
            Menu
          </h2>
          <div className="space-y-1">
            <Link href="/dashboard">
              <Button
                variant={pathname === "/dashboard" ? "secondary" : "ghost"}
                className="w-full justify-start"
              >
                <LayoutDashboard className="mr-2 h-4 w-4" />
                Dashboard
              </Button>
            </Link>
            <Link href="/library">
              <Button
                variant={pathname === "/library" ? "secondary" : "ghost"}
                className="w-full justify-start"
              >
                <Library className="mr-2 h-4 w-4" />
                Library
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
