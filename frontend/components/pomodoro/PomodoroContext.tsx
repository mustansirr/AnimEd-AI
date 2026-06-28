"use client";

import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from "react";

export type TimerMode = "work" | "shortBreak" | "longBreak";

export interface PomodoroSettings {
  work: number;
  shortBreak: number;
  longBreak: number;
}

interface PomodoroContextType {
  settings: PomodoroSettings;
  mode: TimerMode;
  timeLeft: number;
  isActive: boolean;
  sessionsCompleted: number;
  soundEnabled: boolean;
  updateSetting: (key: keyof PomodoroSettings, value: number) => void;
  toggleSound: () => void;
  toggleTimer: () => void;
  resetTimer: () => void;
  handleModeSwitch: (newMode: TimerMode) => void;
}

const DEFAULT_SETTINGS: PomodoroSettings = {
  work: 25,
  shortBreak: 5,
  longBreak: 15,
};

const PomodoroContext = createContext<PomodoroContextType | undefined>(undefined);

export function PomodoroProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<PomodoroSettings>(DEFAULT_SETTINGS);
  const [mode, setMode] = useState<TimerMode>("work");
  const [timeLeft, setTimeLeft] = useState(DEFAULT_SETTINGS.work * 60);
  const [isActive, setIsActive] = useState(false);
  const [sessionsCompleted, setSessionsCompleted] = useState(0);
  const [soundEnabled, setSoundEnabled] = useState(true);

  const audioCtxRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("pomodoroSettings");
    const savedSound = localStorage.getItem("pomodoroSound");
    
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSettings(parsed);
        // We only set timeLeft to saved if it hasn't been modified yet
        // However, a simple approach is just setting it if we're not active
        if (!isActive) {
           setTimeLeft(parsed.work * 60);
        }
      } catch (e) {
        console.error("Failed to parse settings", e);
      }
    }
    
    if (savedSound) {
      setSoundEnabled(savedSound === "true");
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const updateSetting = (key: keyof PomodoroSettings, value: number) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    localStorage.setItem("pomodoroSettings", JSON.stringify(newSettings));
    
    if (!isActive && mode === key) {
      setTimeLeft(value * 60);
    }
  };

  const toggleSound = () => {
    const newSound = !soundEnabled;
    setSoundEnabled(newSound);
    localStorage.setItem("pomodoroSound", String(newSound));
  };

  const playBeep = useCallback(() => {
    if (!soundEnabled) return;
    
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') {
        ctx.resume();
      }
      
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      
      osc.type = "sine";
      osc.frequency.setValueAtTime(880, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.5);
      
      gain.gain.setValueAtTime(0, ctx.currentTime);
      gain.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.1);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.8);
      
      osc.connect(gain);
      gain.connect(ctx.destination);
      
      osc.start();
      osc.stop(ctx.currentTime + 0.8);
    } catch (e) {
      console.error("Audio playback failed", e);
    }
  }, [soundEnabled]);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (isActive && timeLeft === 0) {
      playBeep();
      handleSessionComplete();
    }

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isActive, timeLeft, playBeep]);

  const handleSessionComplete = () => {
    if (mode === "work") {
      const newCompleted = sessionsCompleted + 1;
      setSessionsCompleted(newCompleted);
      
      if (newCompleted % 4 === 0) {
        setMode("longBreak");
        setTimeLeft(settings.longBreak * 60);
      } else {
        setMode("shortBreak");
        setTimeLeft(settings.shortBreak * 60);
      }
    } else {
      setMode("work");
      setTimeLeft(settings.work * 60);
    }
  };

  const toggleTimer = () => {
    if (!isActive && audioCtxRef.current?.state === 'suspended') {
      audioCtxRef.current.resume();
    }
    setIsActive(!isActive);
  };

  const resetTimer = () => {
    setIsActive(false);
    setTimeLeft(settings[mode] * 60);
  };

  const handleModeSwitch = (newMode: TimerMode) => {
    setMode(newMode);
    setTimeLeft(settings[newMode] * 60);
    setIsActive(false);
  };

  const value = {
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
  };

  return (
    <PomodoroContext.Provider value={value}>
      {children}
    </PomodoroContext.Provider>
  );
}

export function usePomodoro() {
  const context = useContext(PomodoroContext);
  if (context === undefined) {
    throw new Error("usePomodoro must be used within a PomodoroProvider");
  }
  return context;
}
