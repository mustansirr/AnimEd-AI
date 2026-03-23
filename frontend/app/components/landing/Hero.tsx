"use client";

import { useState, useEffect } from "react";
import { signInWithGoogle } from "@/app/auth/actions";
import { Sparkles } from "lucide-react";

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      {/* Animated background blobs — soft pastels for light theme */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 -left-32 w-96 h-96 rounded-full bg-violet-200/40 blur-[120px] animate-blob-float" />
        <div
          className="absolute top-1/3 right-0 w-[500px] h-[500px] rounded-full bg-indigo-200/30 blur-[120px] animate-blob-float"
          style={{ animationDelay: "2s" }}
        />
        <div
          className="absolute bottom-0 left-1/3 w-[400px] h-[400px] rounded-full bg-blue-200/30 blur-[120px] animate-blob-float"
          style={{ animationDelay: "4s" }}
        />
        <div
          className="absolute top-10 right-1/4 w-64 h-64 rounded-full bg-purple-200/20 blur-[100px] animate-blob-float"
          style={{ animationDelay: "6s" }}
        />
      </div>

      {/* Grid pattern overlay */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(0,0,0,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,0.08) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      {/* Content */}
      <div className="relative z-10 mx-auto max-w-5xl px-6 text-center">
        {/* Badge */}
        <div className="animate-fade-in-up mb-8 inline-flex items-center gap-2 rounded-full border border-violet-200 bg-violet-50 px-4 py-1.5 text-sm text-violet-700 backdrop-blur-sm">
          <Sparkles size={14} className="text-violet-500" />
          <span>Powered by AI Agents</span>
        </div>

        {/* Headline */}
        <h1 className="animate-fade-in-up font-[family-name:var(--font-inter)] text-5xl font-extrabold leading-tight tracking-tight text-gray-900 sm:text-6xl lg:text-7xl">
          Turn Your Ideas Into{" "}
          <span className="gradient-text">Educational Videos</span>{" "}
          Instantly
        </h1>

        {/* Subheading */}
        <p className="animate-fade-in-up delay-200 mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-gray-500 sm:text-xl opacity-0" style={{ animationFillMode: "forwards" }}>
          Transform any topic into engaging, animated educational content in
          minutes. Just type your prompt and let our AI agents handle the rest.
        </p>

        {/* Interactive prompt input */}
        <div className="animate-fade-in-up delay-400 mx-auto mt-10 max-w-2xl opacity-0" style={{ animationFillMode: "forwards" }}>
          <div className="glass-card p-2 flex items-center gap-2 sm:flex-row flex-col">
            <div className="flex-1 w-full">
              <div className="flex items-center gap-3 rounded-xl bg-gray-50 px-5 py-4">
                <Sparkles size={18} className="text-violet-500 shrink-0" />
                <TypingPlaceholder />
              </div>
            </div>
            <form action={signInWithGoogle}>
              <button
                type="submit"
                className="glow-button whitespace-nowrap rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-8 py-4 text-sm font-semibold text-white hover:from-violet-500 hover:to-indigo-500 transition-all duration-300 cursor-pointer sm:w-auto w-full"
              >
                Generate Video →
              </button>
            </form>
          </div>
        </div>

        {/* Trust indicators */}
        <div className="animate-fade-in-up delay-700 mt-8 flex items-center justify-center gap-6 text-sm text-gray-400 opacity-0" style={{ animationFillMode: "forwards" }}>
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
            Free to try
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
            No credit card required
          </span>
          <span className="hidden sm:flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
            AI-generated in minutes
          </span>
        </div>
      </div>
    </section>
  );
}

/* Typing animation component */
function TypingPlaceholder() {
  const prompts = [
    "Explain photosynthesis with animations...",
    "How do chemical bonds work?",
    "Show the solar system in motion...",
    "Explain Newton's laws of motion...",
  ];

  return <TypingAnimation prompts={prompts} />;
}

function TypingAnimation({ prompts }: { prompts: string[] }) {
  const [displayText, setDisplayText] = useState("");
  const [promptIndex, setPromptIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentPrompt = prompts[promptIndex];

    const timeout = setTimeout(
      () => {
        if (!isDeleting) {
          if (charIndex < currentPrompt.length) {
            setDisplayText(currentPrompt.substring(0, charIndex + 1));
            setCharIndex(charIndex + 1);
          } else {
            setTimeout(() => setIsDeleting(true), 2000);
          }
        } else {
          if (charIndex > 0) {
            setDisplayText(currentPrompt.substring(0, charIndex - 1));
            setCharIndex(charIndex - 1);
          } else {
            setIsDeleting(false);
            setPromptIndex((promptIndex + 1) % prompts.length);
          }
        }
      },
      isDeleting ? 30 : 60
    );

    return () => clearTimeout(timeout);
  }, [charIndex, isDeleting, promptIndex, prompts]);

  return (
    <span className="text-gray-400 text-left block">
      {displayText}
      <span className="animate-cursor-blink text-violet-500 ml-0.5">|</span>
    </span>
  );
}
