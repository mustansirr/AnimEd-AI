"use client";

import { ReactNode } from "react";
import { VideoProvider } from "@/components/dashboard/VideoContext";

interface DashboardWrapperProps {
  children: ReactNode;
}

export function DashboardWrapper({ children }: DashboardWrapperProps) {
  return <VideoProvider>{children}</VideoProvider>;
}
