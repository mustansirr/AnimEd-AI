"use client";

import React, { useState, useEffect } from "react";
import { Play, Pause, RotateCcw, Settings2, X, Volume2, VolumeX } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { usePomodoro, TimerMode } from "./PomodoroContext";

export function PomodoroTimer() {
  const [isClient, setIsClient] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  
  const {
    settings,
    mode,
    timeLeft,
    isActive,
    sessionsCompleted,
    soundEnabled,
    updateSetting,
    toggleSound,
    toggleTimer,
    resetTimer,
    handleModeSwitch
  } = usePomodoro();

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) return null;

  // Format time (MM:SS)
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;
  const timeString = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  
  // Calculate progress for circular indicator
  const totalSeconds = settings[mode] * 60;
  const progress = ((totalSeconds - timeLeft) / totalSeconds) * 100;
  const strokeDasharray = 283; // 2 * pi * r (where r=45)
  const strokeDashoffset = strokeDasharray - (strokeDasharray * progress) / 100;

  // Theme based on mode
  // The user requested to "remove that white glow in the 'work' timer."
  // Previously we used: bg: "bg-[#FFDFDF]", gradient: "from-[#F875AA]/20 to-[#FFDFDF]/5"
  // Let's remove the background completely or make it transparent so there's no glow.
  const themeConfig = {
    work: {
      color: "text-[#F875AA]",
      bg: "bg-transparent",
      stroke: "stroke-[#F875AA]"
    },
    shortBreak: {
      color: "text-emerald-500",
      bg: "bg-emerald-100 dark:bg-emerald-900/30",
      stroke: "stroke-emerald-500"
    },
    longBreak: {
      color: "text-blue-500",
      bg: "bg-blue-100 dark:bg-blue-900/30",
      stroke: "stroke-blue-500"
    }
  };

  const theme = themeConfig[mode];

  return (
    <div className="flex flex-col items-center max-w-lg mx-auto w-full">
      {/* Mode Selector */}
      <div className="flex items-center gap-2 p-1.5 bg-white/50 dark:bg-slate-800/50 backdrop-blur-md rounded-full shadow-sm mb-12 border border-slate-200 dark:border-slate-700">
        <ModeButton 
          active={mode === "work"} 
          onClick={() => handleModeSwitch("work")}
          activeClassName="bg-[#F875AA] text-white shadow-md"
        >
          Work
        </ModeButton>
        <ModeButton 
          active={mode === "shortBreak"} 
          onClick={() => handleModeSwitch("shortBreak")}
          activeClassName="bg-emerald-500 text-white shadow-md"
        >
          Short Break
        </ModeButton>
        <ModeButton 
          active={mode === "longBreak"} 
          onClick={() => handleModeSwitch("longBreak")}
          activeClassName="bg-blue-500 text-white shadow-md"
        >
          Long Break
        </ModeButton>
      </div>

      {/* Main Timer Display */}
      <div className="relative flex items-center justify-center mb-12 group">
        {/* Animated Glow */}
        <div className={cn(
          "absolute inset-0 rounded-full blur-3xl opacity-20 transition-all duration-1000",
          theme.bg,
          isActive && mode !== "work" && "animate-pulse opacity-40"
        )} />
        
        {/* SVG Progress Circle */}
        <svg className="w-72 h-72 transform -rotate-90 relative z-10" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="transparent"
            strokeWidth="3"
            className="stroke-slate-200 dark:stroke-slate-800"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="transparent"
            strokeWidth="4"
            strokeLinecap="round"
            className={cn("transition-all duration-1000 ease-linear", theme.stroke)}
            style={{
              strokeDasharray,
              strokeDashoffset
            }}
          />
        </svg>

        {/* Time Text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center z-20">
          <span className={cn(
            "text-7xl font-light tracking-tight transition-colors duration-500",
            theme.color
          )}>
            {timeString}
          </span>
          <span className="text-slate-500 dark:text-slate-400 font-medium uppercase tracking-widest text-sm mt-2">
            {mode === "work" ? "Focus" : "Relax"}
          </span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-6 mb-12">
        <Button
          variant="outline"
          size="icon"
          className="h-12 w-12 rounded-full border-slate-200 dark:border-slate-700 bg-white/50 dark:bg-slate-800/50 backdrop-blur hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 transition-all"
          onClick={resetTimer}
        >
          <RotateCcw className="h-5 w-5" />
        </Button>
        
        <Button
          onClick={toggleTimer}
          className={cn(
            "h-20 w-20 rounded-full shadow-xl transition-all duration-300 hover:scale-105 active:scale-95",
            isActive 
              ? "bg-slate-800 hover:bg-slate-900 text-white dark:bg-white dark:hover:bg-slate-200 dark:text-slate-900 shadow-slate-900/20" 
              : `bg-white hover:bg-slate-50 text-slate-900 shadow-xl border border-slate-100 dark:bg-slate-800 dark:hover:bg-slate-700 dark:border-slate-700 dark:text-white`
          )}
        >
          {isActive ? (
            <Pause className="h-8 w-8 fill-current" />
          ) : (
            <Play className={cn("h-8 w-8 ml-1 fill-current", theme.color)} />
          )}
        </Button>

        <Button
          variant="outline"
          size="icon"
          className={cn(
            "h-12 w-12 rounded-full border-slate-200 dark:border-slate-700 backdrop-blur transition-all",
            showSettings 
              ? "bg-slate-800 text-white border-slate-800 dark:bg-white dark:text-slate-900" 
              : "bg-white/50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300"
          )}
          onClick={() => setShowSettings(!showSettings)}
        >
          {showSettings ? <X className="h-5 w-5" /> : <Settings2 className="h-5 w-5" />}
        </Button>
      </div>

      {/* Session Tracker */}
      <div className="flex flex-col items-center gap-3">
        <div className="flex items-center gap-2">
          {Array.from({ length: Math.max(4, sessionsCompleted) }).map((_, i) => (
            <span 
              key={i} 
              className={cn(
                "text-2xl transition-all duration-500",
                i < sessionsCompleted ? "opacity-100 scale-100 filter-none" : "opacity-30 scale-75 grayscale"
              )}
            >
              🍅
            </span>
          ))}
        </div>
        <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">
          {sessionsCompleted} {sessionsCompleted === 1 ? "session" : "sessions"} completed
        </p>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="w-full mt-12 p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xl animate-in fade-in slide-in-from-bottom-4 duration-300">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-semibold text-slate-900 dark:text-white">Timer Settings (minutes)</h3>
            <Button variant="ghost" size="icon" onClick={toggleSound} className="text-slate-500 rounded-full">
              {soundEnabled ? <Volume2 className="h-5 w-5" /> : <VolumeX className="h-5 w-5" />}
            </Button>
          </div>
          
          <div className="grid grid-cols-3 gap-6">
            <SettingInput
              label="Work"
              value={settings.work}
              onChange={(v) => updateSetting("work", v)}
              themeColor="text-[#F875AA]"
            />
            <SettingInput
              label="Short Break"
              value={settings.shortBreak}
              onChange={(v) => updateSetting("shortBreak", v)}
              themeColor="text-emerald-500"
            />
            <SettingInput
              label="Long Break"
              value={settings.longBreak}
              onChange={(v) => updateSetting("longBreak", v)}
              themeColor="text-blue-500"
            />
          </div>
        </div>
      )}
    </div>
  );
}

// Subcomponents

function ModeButton({ 
  children, 
  active, 
  onClick, 
  activeClassName 
}: { 
  children: React.ReactNode; 
  active: boolean; 
  onClick: () => void;
  activeClassName: string;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "px-5 py-2 rounded-full text-sm font-medium transition-all duration-300",
        active 
          ? activeClassName 
          : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50"
      )}
    >
      {children}
    </button>
  );
}

function SettingInput({ 
  label, 
  value, 
  onChange,
  themeColor
}: { 
  label: string; 
  value: number; 
  onChange: (val: number) => void;
  themeColor: string;
}) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
        {label}
      </label>
      <input
        type="number"
        min="1"
        max="90"
        value={value}
        onChange={(e) => {
          const val = parseInt(e.target.value);
          if (!isNaN(val) && val > 0) onChange(val);
        }}
        className={cn(
          "w-full bg-slate-50 dark:bg-slate-800 border-none rounded-lg p-3 text-lg font-semibold focus:ring-2 focus:ring-opacity-50 transition-shadow outline-none text-slate-900 dark:text-white",
          themeColor && `focus:ring-${themeColor.split('-')[1]}-500`
        )}
        style={{
          boxShadow: 'none'
        }}
      />
    </div>
  );
}
