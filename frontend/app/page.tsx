import { createClient } from "@/utils/supabase/server";
import { redirect } from "next/navigation";
import Navbar from "./components/landing/Navbar";
import Hero from "./components/landing/Hero";
import Features from "./components/landing/Features";
import HowItWorks from "./components/landing/HowItWorks";
import Demo from "./components/landing/Demo";
import SocialProof from "./components/landing/SocialProof";
import CTA from "./components/landing/CTA";
import Footer from "./components/landing/Footer";

export default async function Home() {
  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (user) {
    redirect("/dashboard");
  }

  return (
    <main className="min-h-screen bg-[#fafbff] text-gray-900 overflow-x-hidden">
      <Navbar />
      <Hero />
      <Features />
      <HowItWorks />
      <Demo />
      <SocialProof />
      <CTA />
      <Footer />
    </main>
  );
}
