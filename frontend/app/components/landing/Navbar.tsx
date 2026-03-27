"use client";

import { useState } from "react";
import { signInWithGoogle } from "@/app/auth/actions";
import { Menu, X } from "lucide-react";

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const navLinks = [
    { label: "Features", href: "#features" },
    { label: "How It Works", href: "#how-it-works" },
    { label: "Demo", href: "#demo" },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-nav">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <a href="#" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-[#F875AA] to-[#AEDEFC] flex items-center justify-center">
              <span className="text-white font-bold text-sm">M</span>
            </div>
            <span className="text-xl font-bold gradient-text font-[family-name:var(--font-inter)]">
              Manima
            </span>
          </a>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="text-sm text-gray-500 hover:text-gray-900 transition-colors duration-200"
              >
                {link.label}
              </a>
            ))}
            <form action={signInWithGoogle}>
              <button
                type="submit"
                className="rounded-full bg-gradient-to-r from-[#F875AA] to-[#e8609a] px-5 py-2 text-sm font-medium text-white hover:from-[#f56da0] hover:to-[#d4558a] transition-all duration-200 shadow-lg shadow-[#F875AA]/20"
              >
                Get Started
              </button>
            </form>
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden text-gray-500 hover:text-gray-900 transition-colors"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden py-4 border-t border-gray-100">
            <div className="flex flex-col gap-4">
              {navLinks.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  className="text-sm text-gray-500 hover:text-gray-900 transition-colors duration-200 py-2"
                  onClick={() => setMobileOpen(false)}
                >
                  {link.label}
                </a>
              ))}
              <form action={signInWithGoogle}>
                <button
                  type="submit"
                  className="w-full rounded-full bg-gradient-to-r from-[#F875AA] to-[#e8609a] px-5 py-2.5 text-sm font-medium text-white hover:from-[#f56da0] hover:to-[#d4558a] transition-all duration-200"
                >
                  Get Started
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
