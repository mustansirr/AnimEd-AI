import { Github, Twitter } from "lucide-react";
import Image from "next/image";

export default function Footer() {
  const links = [
    { label: "Features", href: "#features" },
    { label: "How It Works", href: "#how-it-works" },
    { label: "Demo", href: "#demo" },
  ];

  const legalLinks = [
    { label: "Privacy", href: "#" },
    { label: "Terms", href: "#" },
    { label: "Contact", href: "#" },
  ];

  return (
    <footer className="relative border-t border-gray-100 bg-white">
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-12">
          <div className="max-w-xs">
            <div className="flex items-center gap-2 mb-4">
              <Image
                src="/animed-logo.png"
                alt="AnimEd AI Logo"
                width={120}
                height={32}
                className="h-8 w-auto"
              />
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">
              AI-powered educational video generation. Transform any topic into engaging animated content.
            </p>
          </div>
          <div className="flex gap-16">
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-4">Product</h4>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link.label}>
                    <a href={link.href} className="text-sm text-gray-400 hover:text-gray-700 transition-colors duration-200">{link.label}</a>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-4">Legal</h4>
              <ul className="space-y-3">
                {legalLinks.map((link) => (
                  <li key={link.label}>
                    <a href={link.href} className="text-sm text-gray-400 hover:text-gray-700 transition-colors duration-200">{link.label}</a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div className="flex gap-4">
            <a href="#" className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-50 text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-all duration-200" aria-label="GitHub">
              <Github size={18} />
            </a>
            <a href="#" className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-50 text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-all duration-200" aria-label="Twitter">
              <Twitter size={18} />
            </a>
          </div>
        </div>
        <div className="mt-12 pt-8 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-gray-400">&copy; {new Date().getFullYear()} AnimEd AI. Made with ❤️ by Team AnimEd AI.</p>
          <p className="text-xs text-gray-400">Academic project — For educational use only.</p>
        </div>
      </div>
    </footer>
  );
}
