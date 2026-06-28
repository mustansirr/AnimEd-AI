"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, BrainCircuit, Library, Clock } from "lucide-react";
import { DashboardWrapper } from "@/components/dashboard/DashboardWrapper";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { Button } from "@/components/ui/button";
import { createClient } from "@/utils/supabase/client";
import { getDecks, FlashcardDeck } from "@/lib/api";
import { CreateDeckModal } from "@/components/flashcards/CreateDeckModal";

export default function FlashcardsPage() {
  const [decks, setDecks] = useState<FlashcardDeck[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    async function loadDecks() {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        setUserId(user.id);
        try {
          const fetchedDecks = await getDecks(user.id);
          setDecks(fetchedDecks);
        } catch (e) {
          console.error("Failed to load decks", e);
        }
      }
      setLoading(false);
    }
    loadDecks();
  }, []);

  const handleCreateDeck = async (title: string, description: string) => {
    if (!userId) return;
    const { createDeck } = await import("@/lib/api");
    const newDeck = await createDeck(userId, title, description);
    setDecks([newDeck, ...decks]);
  };

  return (
    <DashboardWrapper>
      <div className="flex min-h-screen bg-[#FFF6F6] dark:bg-background font-sans text-gray-900 dark:text-foreground relative transition-colors">
        <div className="fixed inset-0 z-0 bg-[linear-gradient(to_right,#FFDFDF_1px,transparent_1px),linear-gradient(to_bottom,#FFDFDF_1px,transparent_1px)] dark:bg-[linear-gradient(to_right,rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

        <Sidebar className="hidden md:block w-64 flex-shrink-0 z-10" />
        
        <div className="flex-1 flex flex-col min-w-0 h-screen z-10 relative">
          <Header />

          <main className="flex-1 overflow-y-auto px-4 md:px-8 py-8">
            <div className="max-w-6xl mx-auto">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-foreground">Flashcards</h1>
                  <p className="text-gray-500 dark:text-muted-foreground mt-1">Master your subjects with spaced repetition</p>
                </div>
                <Button 
                  onClick={() => setIsCreateModalOpen(true)}
                  className="bg-[#e8609a] hover:bg-[#d64a85] text-white flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  New Deck
                </Button>
              </div>

              {loading ? (
                <div className="flex justify-center items-center h-64">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#e8609a]"></div>
                </div>
              ) : decks.length === 0 ? (
                <div className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-12 text-center">
                  <div className="w-16 h-16 bg-[#FFDFDF] dark:bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Library className="w-8 h-8 text-[#e8609a] dark:text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-foreground mb-2">No decks yet</h3>
                  <p className="text-gray-500 dark:text-muted-foreground mb-6 max-w-md mx-auto">
                    Create your first flashcard deck to start studying. You can generate flashcards automatically using AI or add them manually.
                  </p>
                  <Button 
                    onClick={() => setIsCreateModalOpen(true)}
                    className="bg-[#e8609a] hover:bg-[#d64a85] text-white"
                  >
                    Create your first deck
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {decks.map(deck => (
                    <Link key={deck.id} href={`/flashcards/${deck.id}`}>
                      <div className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-6 hover:shadow-md transition-all group h-full flex flex-col">
                        <div className="flex items-start justify-between mb-4">
                          <div className="w-10 h-10 rounded-lg bg-pink-50 dark:bg-primary/10 flex items-center justify-center">
                            <BrainCircuit className="w-5 h-5 text-[#e8609a] dark:text-primary" />
                          </div>
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-foreground mb-2 group-hover:text-[#e8609a] transition-colors">{deck.title}</h3>
                        <p className="text-gray-500 dark:text-muted-foreground text-sm flex-1 line-clamp-2">
                          {deck.description || "No description provided."}
                        </p>
                        <div className="mt-6 pt-4 border-t border-gray-100 dark:border-border flex items-center text-xs text-gray-400 dark:text-muted-foreground">
                          <Clock className="w-3 h-3 mr-1" />
                          Created {new Date(deck.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </main>
        </div>
      </div>
      <CreateDeckModal 
        isOpen={isCreateModalOpen} 
        onClose={() => setIsCreateModalOpen(false)} 
        onCreate={handleCreateDeck} 
      />
    </DashboardWrapper>
  );
}
