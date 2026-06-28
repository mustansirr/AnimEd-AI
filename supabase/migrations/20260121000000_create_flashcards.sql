-- Create Flashcard Decks Table
CREATE TABLE flashcard_decks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS for flashcard_decks
ALTER TABLE flashcard_decks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own decks"
    ON flashcard_decks FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own decks"
    ON flashcard_decks FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own decks"
    ON flashcard_decks FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own decks"
    ON flashcard_decks FOR DELETE
    USING (auth.uid() = user_id);


-- Create Flashcards Table
CREATE TABLE flashcards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deck_id UUID NOT NULL REFERENCES flashcard_decks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    next_review_date TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    interval INTEGER DEFAULT 0 NOT NULL,
    ease_factor REAL DEFAULT 2.5 NOT NULL,
    repetitions INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS for flashcards
ALTER TABLE flashcards ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own flashcards"
    ON flashcards FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own flashcards"
    ON flashcards FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own flashcards"
    ON flashcards FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own flashcards"
    ON flashcards FOR DELETE
    USING (auth.uid() = user_id);

-- Create triggers to update updated_at
CREATE TRIGGER set_updated_at_flashcard_decks
    BEFORE UPDATE ON flashcard_decks
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER set_updated_at_flashcards
    BEFORE UPDATE ON flashcards
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();
