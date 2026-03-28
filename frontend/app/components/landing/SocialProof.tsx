"use client";

import { useEffect, useRef } from "react";
import { Video, GraduationCap, BookOpen, Star } from "lucide-react";

const stats = [
  { icon: Video, value: "10K+", label: "Videos Generated" },
  { icon: GraduationCap, value: "500+", label: "Educators" },
  { icon: BookOpen, value: "50+", label: "Subjects Covered" },
];

const testimonials = [
  {
    name: "Dr. Sarah Chen",
    role: "Chemistry Professor",
    quote:
      "AnimEd AI transformed my lecture prep. What used to take hours of animation work now takes minutes. My students love the visual explanations.",
    avatar: "SC",
    gradient: "from-[#F875AA] to-[#e8609a]",
  },
  {
    name: "Rahul Patel",
    role: "High School Science Teacher",
    quote:
      "The quality of animations is incredible. It feels like having a professional animation studio at my fingertips. Game changer for STEM education.",
    avatar: "RP",
    gradient: "from-[#AEDEFC] to-[#8dcef5]",
  },
  {
    name: "Emily Rodriguez",
    role: "EdTech Content Creator",
    quote:
      "I've tried many tools, but AnimEd AI's agents create explanations that actually make sense. The curriculum alignment feature is brilliant.",
    avatar: "ER",
    gradient: "from-[#F875AA]/80 to-[#AEDEFC]",
  },
];

export default function SocialProof() {
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
    <section ref={sectionRef} className="relative py-32 overflow-hidden bg-gray-50/50">
      {/* Background glow */}
      <div className="absolute bottom-0 left-1/4 w-[600px] h-[400px] rounded-full bg-[#FFDFDF]/30 blur-[150px]" />

      <div className="relative z-10 mx-auto max-w-7xl px-6 lg:px-8">
        {/* Section header */}
        <div className="reveal mx-auto max-w-2xl text-center mb-16">
          <span className="inline-block mb-4 text-sm font-medium text-[#F875AA] tracking-wider uppercase">
            Trusted by Educators
          </span>
          <h2 className="font-[family-name:var(--font-inter)] text-4xl font-bold text-gray-900 sm:text-5xl tracking-tight">
            Loved by <span className="gradient-text">Students & Teachers</span>
          </h2>
        </div>

        {/* Stats */}
        <div className="reveal grid grid-cols-1 gap-6 sm:grid-cols-3 mb-20">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="glass-card flex flex-col items-center p-8 text-center transition-all duration-300 hover:-translate-y-1"
            >
              <stat.icon size={24} className="text-[#F875AA] mb-4" />
              <span className="text-4xl font-bold text-gray-900 mb-2 font-[family-name:var(--font-inter)]">
                {stat.value}
              </span>
              <span className="text-sm text-gray-500">{stat.label}</span>
            </div>
          ))}
        </div>

        {/* Testimonials */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {testimonials.map((testimonial, index) => (
            <div
              key={testimonial.name}
              className="reveal"
              style={{ transitionDelay: `${index * 100}ms` }}
            >
              <div className="glass-card h-full p-8 transition-all duration-300 hover:-translate-y-1">
                {/* Stars */}
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      size={14}
                      className="text-amber-400"
                      fill="currentColor"
                    />
                  ))}
                </div>

                {/* Quote */}
                <p className="text-gray-600 text-sm leading-relaxed mb-6">
                  &ldquo;{testimonial.quote}&rdquo;
                </p>

                {/* Author */}
                <div className="flex items-center gap-3">
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br ${testimonial.gradient} text-sm font-semibold text-white`}
                  >
                    {testimonial.avatar}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {testimonial.name}
                    </p>
                    <p className="text-xs text-gray-400">
                      {testimonial.role}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
