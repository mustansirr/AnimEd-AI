"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { ArrowLeft, Plus, BrainCircuit, Play, Pencil, Trash2 } from "lucide-react";
import { DashboardWrapper } from "@/components/dashboard/DashboardWrapper";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { Button } from "@/components/ui/button";
import { createClient } from "@/utils/supabase/client";
import { getDeckCards, Flashcard, getDecks, FlashcardDeck } from "@/lib/api";
import { CreateFlashcardModal } from "@/components/flashcards/CreateFlashcardModal";
import { FlashcardStudyModal } from "@/components/flashcards/FlashcardStudyModal";
import { EditDeckModal } from "@/components/flashcards/EditDeckModal";

export default function DeckPage({ params }: { params: Promise<{ deckId: string }> }) {
  const { deckId } = use(params);
  
  const [deck, setDeck] = useState<FlashcardDeck | null>(null);
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<string | null>(null);
  
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isStudyModalOpen, setIsStudyModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  useEffect(() => {
    async function loadData() {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        setUserId(user.id);
        try {
          const fetchedDecks = await getDecks(user.id);
          const currentDeck = fetchedDecks.find(d => d.id === deckId);
          if (currentDeck) {
            setDeck(currentDeck);
          }
          
          const fetchedCards = await getDeckCards(deckId);
          setCards(fetchedCards);
        } catch (e) {
          console.error("Failed to load deck data", e);
        }
      }
      setLoading(false);
    }
    loadData();
  }, [deckId]);

  const dueCards = cards.filter(c => new Date(c.next_review_date) <= new Date());

  const handleManualCreate = async (front: string, back: string) => {
    if (!userId) return;
    const { createCard } = await import("@/lib/api");
    const newCard = await createCard(userId, deckId, front, back);
    setCards([...cards, newCard]);
  };

  const handleAIGenerate = async (topic: string, count: number) => {
    if (!userId) return;
    const { generateCards } = await import("@/lib/api");
    const newCards = await generateCards(userId, deckId, topic, count);
    setCards([...cards, ...newCards]);
  };

  const handleReview = async (cardId: string, rating: number) => {
    const { reviewCard } = await import("@/lib/api");
    const updatedCard = await reviewCard(cardId, rating);
    setCards(cards.map(c => c.id === cardId ? updatedCard : c));
  };

  const handleEditDeck = async (title: string, description: string) => {
    if (!userId || !deck) return;
    const { updateDeck } = await import("@/lib/api");
    const updatedDeck = await updateDeck(userId, deckId, title, description);
    setDeck(updatedDeck);
  };

  const handleDeleteDeck = async () => {
    if (!userId || !deck) return;
    const { deleteDeck } = await import("@/lib/api");
    await deleteDeck(userId, deckId);
    window.location.href = "/flashcards";
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
              
              <Link href="/flashcards" className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-[#e8609a] mb-6 transition-colors">
                <ArrowLeft className="w-4 h-4 mr-1" />
                Back to Decks
              </Link>

              {loading ? (
                <div className="flex justify-center items-center h-64">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#e8609a]"></div>
                </div>
              ) : !deck ? (
                <div className="text-center py-20">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-foreground">Deck not found</h2>
                  <p className="text-gray-500 mt-2">The deck you are looking for does not exist or you don't have access.</p>
                </div>
              ) : (
                <>
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4">
                    <div>
                      <div className="flex items-center gap-3">
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-foreground">{deck.title}</h1>
                        <button onClick={() => setIsEditModalOpen(true)} className="text-gray-400 hover:text-[#e8609a] transition-colors" title="Edit Deck">
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button onClick={handleDeleteDeck} className="text-gray-400 hover:text-red-500 transition-colors" title="Delete Deck">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <p className="text-gray-500 dark:text-muted-foreground mt-2 max-w-2xl">{deck.description}</p>
                      
                      <div className="flex items-center gap-4 mt-4 text-sm">
                        <span className="bg-gray-100 dark:bg-muted text-gray-700 dark:text-foreground px-3 py-1 rounded-full font-medium">
                          {cards.length} Total Cards
                        </span>
                        <span className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-3 py-1 rounded-full font-medium">
                          {dueCards.length} Due for Review
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <Button 
                        onClick={() => setIsCreateModalOpen(true)}
                        variant="outline"
                        className="border-gray-300 dark:border-border text-gray-700 dark:text-foreground hover:bg-gray-100 dark:hover:bg-muted flex items-center gap-2"
                      >
                        <Plus className="w-4 h-4" />
                        Add Cards
                      </Button>
                      <Button 
                        onClick={() => setIsStudyModalOpen(true)}
                        disabled={cards.length === 0}
                        className="bg-[#e8609a] hover:bg-[#d64a85] text-white flex items-center gap-2 shadow-sm"
                      >
                        <Play className="w-4 h-4" />
                        Study Now
                      </Button>
                    </div>
                  </div>

                  {cards.length === 0 ? (
                    <div className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-12 text-center mt-8">
                      <div className="w-16 h-16 bg-[#FFDFDF] dark:bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <BrainCircuit className="w-8 h-8 text-[#e8609a] dark:text-primary" />
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 dark:text-foreground mb-2">This deck is empty</h3>
                      <p className="text-gray-500 dark:text-muted-foreground mb-6 max-w-md mx-auto">
                        Add some flashcards to start studying. You can generate them with AI!
                      </p>
                      <Button 
                        onClick={() => setIsCreateModalOpen(true)}
                        className="bg-[#e8609a] hover:bg-[#d64a85] text-white"
                      >
                        Add Flashcards
                      </Button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
                      {cards.map(card => {
                        const isDue = new Date(card.next_review_date) <= new Date();
                        return (
                          <div key={card.id} className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-6 hover:shadow-sm transition-shadow flex flex-col relative overflow-hidden">
                            {isDue && (
                              <div className="absolute top-0 right-0 w-2 h-full bg-green-400"></div>
                            )}
                            <div className="mb-4">
                              <span className="text-xs font-bold text-gray-400 dark:text-muted-foreground uppercase tracking-wider">Front</span>
                              <p className="text-gray-900 dark:text-foreground font-medium mt-1 line-clamp-3">{card.front}</p>
                            </div>
                            <div className="mt-auto pt-4 border-t border-gray-100 dark:border-border">
                              <span className="text-xs font-bold text-gray-400 dark:text-muted-foreground uppercase tracking-wider">Back</span>
                              <p className="text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">{card.back}</p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </>
              )}
            </div>
          </main>
        </div>
      </div>

      <CreateFlashcardModal 
        isOpen={isCreateModalOpen} 
        onClose={() => setIsCreateModalOpen(false)} 
        onManualCreate={handleManualCreate}
        onAIGenerate={handleAIGenerate}
      />

      <FlashcardStudyModal
        isOpen={isStudyModalOpen}
        onClose={() => setIsStudyModalOpen(false)}
        cards={cards}
        onReview={handleReview}
      />

      <EditDeckModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        onEdit={handleEditDeck}
        initialTitle={deck?.title || ""}
        initialDescription={deck?.description || ""}
      />
    </DashboardWrapper>
  );
}
