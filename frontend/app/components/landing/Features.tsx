"use client";

import { useEffect, useRef } from "react";
import { Zap, Brain, Eye, Rocket } from "lucide-react";

const features = [
  {
    icon: Zap,
    title: "Prompt → Video",
    description:
      "Simply type your topic and our AI pipeline generates a complete animated educational video for you.",
    gradient: "from-amber-500 to-orange-600",
    glow: "rgba(245, 158, 11, 0.08)",
  },
  {
    icon: Brain,
    title: "AI-Powered Explanations",
    description:
      "Multiple AI agents collaborate to plan, script, and code animated explanations that make complex topics simple.",
    gradient: "from-violet-500 to-purple-600",
    glow: "rgba(139, 92, 246, 0.08)",
  },
  {
    icon: Eye,
    title: "Visual Animations",
    description:
      "Beautiful Manim-powered mathematical and scientific animations that bring abstract concepts to life.",
    gradient: "from-emerald-500 to-teal-600",
    glow: "rgba(16, 185, 129, 0.08)",
  },
  {
    icon: Rocket,
    title: "Fast & Easy",
    description:
      "From prompt to polished video in minutes. No coding, video editing, or design skills required.",
    gradient: "from-blue-500 to-cyan-600",
    glow: "rgba(59, 130, 246, 0.08)",
  },
];

export default function Features() {
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("revealed");
          }
        });
      },
      { threshold: 0.1 }
    );

    const reveals = sectionRef.current?.querySelectorAll(".reveal");
    reveals?.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  return (
    <section
      id="features"
      ref={sectionRef}
      className="relative py-32 overflow-hidden"
    >
      {/* Subtle background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] rounded-full bg-violet-100/40 blur-[150px]" />

      <div className="relative z-10 mx-auto max-w-7xl px-6 lg:px-8">
        {/* Section header */}
        <div className="reveal mx-auto max-w-2xl text-center mb-20">
          <span className="inline-block mb-4 text-sm font-medium text-violet-600 tracking-wider uppercase">
            Features
          </span>
          <h2 className="font-[family-name:var(--font-inter)] text-4xl font-bold text-gray-900 sm:text-5xl tracking-tight">
            Everything You Need to Create{" "}
            <span className="gradient-text">Amazing Videos</span>
          </h2>
          <p className="mt-6 text-lg text-gray-500 leading-relaxed">
            Our AI-powered pipeline handles every step of the video creation
            process, from scripting to animation rendering.
          </p>
        </div>

        {/* Feature cards grid */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className="reveal group"
              style={{ transitionDelay: `${index * 100}ms` }}
            >
              <div
                className="glass-card h-full p-8 transition-all duration-500 hover:-translate-y-2 cursor-default"
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.boxShadow =
                    `0 20px 60px ${feature.glow}`;
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.boxShadow = "";
                }}
              >
                {/* Icon */}
                <div
                  className={`mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${feature.gradient} shadow-lg`}
                >
                  <feature.icon size={22} className="text-white" />
                </div>

                {/* Title */}
                <h3 className="mb-3 text-lg font-semibold text-gray-900">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-sm leading-relaxed text-gray-500">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
