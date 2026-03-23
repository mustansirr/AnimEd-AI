"use client";

import { useEffect, useRef } from "react";
import { signInWithGoogle } from "@/app/auth/actions";
import { ArrowRight, Sparkles } from "lucide-react";

export default function CTA() {
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
    <section ref={sectionRef} className="relative py-32 overflow-hidden">
      <div className="relative z-10 mx-auto max-w-4xl px-6 lg:px-8">
        <div className="reveal relative rounded-3xl overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-violet-600 via-indigo-600 to-blue-700" />
          <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full bg-white/10 blur-[100px] animate-blob-float" />
          <div className="absolute bottom-0 right-1/4 w-64 h-64 rounded-full bg-white/5 blur-[80px] animate-blob-float" style={{ animationDelay: "3s" }} />
          <div className="absolute inset-0 opacity-5" style={{ backgroundImage: "linear-gradient(rgba(255,255,255,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.3) 1px, transparent 1px)", backgroundSize: "40px 40px" }} />
          <div className="relative z-10 px-8 py-20 sm:px-16 text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm text-white/90 backdrop-blur-sm mb-8">
              <Sparkles size={14} />
              <span>Start creating for free</span>
            </div>
            <h2 className="font-[family-name:var(--font-inter)] text-4xl font-bold text-white sm:text-5xl tracking-tight mb-6">
              Ready to Transform<br />Your Teaching?
            </h2>
            <p className="text-lg text-white/70 mb-10 max-w-xl mx-auto leading-relaxed">
              Join hundreds of educators creating engaging educational content with AI.
            </p>
            <form action={signInWithGoogle} className="inline-block">
              <button type="submit" className="group inline-flex items-center gap-3 rounded-full bg-white px-8 py-4 text-base font-semibold text-indigo-700 hover:bg-white/90 transition-all duration-300 shadow-2xl shadow-black/20 hover:shadow-lg hover:scale-105 cursor-pointer">
                Get Started Free
                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform duration-200" />
              </button>
            </form>
            <p className="mt-6 text-sm text-white/40">No credit card required · Free to try</p>
          </div>
        </div>
      </div>
    </section>
  );
}
