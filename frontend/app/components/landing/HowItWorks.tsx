"use client";

import { useEffect, useRef } from "react";
import { PenLine, Cpu, Play } from "lucide-react";

const steps = [
  {
    id: 1,
    icon: PenLine,
    title: "Enter Your Prompt",
    description:
      "Type any educational topic or concept you want to explain. Upload a PDF or simply describe what you need.",
    gradient: "from-[#F875AA] to-[#e8609a]",
  },
  {
    id: 2,
    icon: Cpu,
    title: "AI Generates Script & Visuals",
    description:
      "Our multi-agent AI pipeline plans the lesson, writes the script, and generates beautiful Manim animations.",
    gradient: "from-[#AEDEFC] to-[#8dcef5]",
  },
  {
    id: 3,
    icon: Play,
    title: "Get Your Educational Video",
    description:
      "Download your polished, curriculum-aligned animated video ready to use in your classroom or share online.",
    gradient: "from-[#F875AA]/80 to-[#AEDEFC]",
  },
];

export default function HowItWorks() {
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
      id="how-it-works"
      ref={sectionRef}
      className="relative py-32 overflow-hidden bg-gray-50/50"
    >
      {/* Background accent */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] rounded-full bg-[#FFDFDF]/40 blur-[150px]" />

      <div className="relative z-10 mx-auto max-w-7xl px-6 lg:px-8">
        {/* Section header */}
        <div className="reveal mx-auto max-w-2xl text-center mb-20">
          <span className="inline-block mb-4 text-sm font-medium text-[#F875AA] tracking-wider uppercase">
            How It Works
          </span>
          <h2 className="font-[family-name:var(--font-inter)] text-4xl font-bold text-gray-900 sm:text-5xl tracking-tight">
            Three Simple Steps to{" "}
            <span className="gradient-text">Your Video</span>
          </h2>
          <p className="mt-6 text-lg text-gray-500 leading-relaxed">
            Creating educational videos has never been easier. Our streamlined
            workflow gets you from idea to video in minutes.
          </p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connecting line (desktop only) */}
          <div className="hidden lg:block absolute top-24 left-[16.66%] right-[16.66%] h-px bg-gradient-to-r from-[#F875AA]/40 via-[#AEDEFC]/60 to-[#F875AA]/40" />

          <div className="grid grid-cols-1 gap-12 lg:grid-cols-3 lg:gap-8">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className="reveal relative flex flex-col items-center text-center"
                style={{ transitionDelay: `${index * 150}ms` }}
              >
                {/* Step number circle */}
                <div className="relative mb-8">
                  <div
                    className={`flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br ${step.gradient} shadow-lg shadow-[#F875AA]/15`}
                  >
                    <step.icon size={32} className="text-white" />
                  </div>
                  {/* Step number badge */}
                  <div className="absolute -top-2 -right-2 flex h-7 w-7 items-center justify-center rounded-full bg-white shadow-md border border-gray-100 text-xs font-bold text-gray-700">
                    {step.id}
                  </div>
                </div>

                {/* Content */}
                <h3 className="mb-3 text-xl font-bold text-gray-900">
                  {step.title}
                </h3>
                <p className="max-w-sm text-gray-500 leading-relaxed">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
