"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Library, LayoutDashboard, Brain } from "lucide-react";
import { cn } from "@/lib/utils";

export function Sidebar({ className }: { className?: string }) {
  const pathname = usePathname();

  return (
    <div className={cn("pb-12 w-64 border-r border-slate-200 dark:border-border bg-white/60 dark:bg-background/60 backdrop-blur-xl min-h-screen hidden md:block transition-colors", className)}>
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <div className="mb-2 px-4">
            <Image
              src="/animed-logo.png"
              alt="AnimEd AI Logo"
              width={120}
              height={32}
              className="h-8 w-auto"
            />
          </div>
        </div>
        <div className="px-3 py-2">
          <h2 className="mb-2 px-4 text-xs font-semibold tracking-tight uppercase text-gray-500 dark:text-muted-foreground">
            Menu
          </h2>
          <div className="space-y-1">
            <Link href="/dashboard">
              <Button
                variant="ghost"
                className={cn(
                  "w-full justify-start font-medium transition-colors",
                  pathname === "/dashboard" 
                    ? "bg-slate-200/80 dark:bg-muted hover:bg-slate-300/80 dark:hover:bg-muted/80 text-slate-900 dark:text-foreground" 
                    : "text-slate-600 dark:text-muted-foreground hover:bg-slate-200/60 dark:hover:bg-muted/50 hover:text-slate-900 dark:hover:text-foreground"
                )}
              >
                <LayoutDashboard className="mr-2 h-4 w-4" />
                Dashboard
              </Button>
            </Link>
            <Link href="/library">
              <Button
                variant="ghost"
                className={cn(
                  "w-full justify-start font-medium transition-colors",
                  pathname === "/library" 
                    ? "bg-slate-200/80 dark:bg-muted hover:bg-slate-300/80 dark:hover:bg-muted/80 text-slate-900 dark:text-foreground" 
                    : "text-slate-600 dark:text-muted-foreground hover:bg-slate-200/60 dark:hover:bg-muted/50 hover:text-slate-900 dark:hover:text-foreground"
                )}
              >
                <Library className="mr-2 h-4 w-4" />
                Library
              </Button>
            </Link>
            <Link href="/flashcards">
              <Button
                variant="ghost"
                className={cn(
                  "w-full justify-start font-medium transition-colors",
                  pathname === "/flashcards" || pathname.startsWith("/flashcards/")
                    ? "bg-slate-200/80 dark:bg-muted hover:bg-slate-300/80 dark:hover:bg-muted/80 text-slate-900 dark:text-foreground" 
                    : "text-slate-600 dark:text-muted-foreground hover:bg-slate-200/60 dark:hover:bg-muted/50 hover:text-slate-900 dark:hover:text-foreground"
                )}
              >
                <Brain className="mr-2 h-4 w-4" />
                Flashcards
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
