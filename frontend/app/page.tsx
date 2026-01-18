import { createClient } from "@/utils/supabase/server";
import { redirect } from "next/navigation";
import Hero from "./components/landing/Hero";
import HowItWorks from "./components/landing/HowItWorks";
import Features from "./components/landing/Features";
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
    <main className="min-h-screen bg-white">
      <Hero />
      <HowItWorks />
      <Features />
      <Footer />
    </main>
  );
}
