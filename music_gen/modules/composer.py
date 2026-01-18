
import random

class MarkovComposer:
    def __init__(self):
        self.chain = {}
        
    def load_data(self):
        """
        Returns a list of simple melodies for training.
        """
        return [
            "C4 C4 G4 G4 A4 A4 G4 F4 F4 E4 E4 D4 D4 C4", # Twinkle Twinkle
            "E4 D4 C4 D4 E4 E4 E4 D4 D4 D4 E4 G4 G4",    # Mary Had a Little Lamb
            "C4 D4 E4 F4 G4 A4 B4 C5 B4 A4 G4 F4 E4 D4 C4", # Scale
            "G4 E4 E4 F4 D4 D4 C4 D4 E4 F4 G4 G4 G4"      # Jingle Bellsish
        ]

    def train(self, melodies):
        """
        Builds a Markov Chain from the provided melodies.
        markov_chain = { 'Note': ['NextPossibleNote1', 'NextPossibleNote2'] }
        """
        self.chain = {}
        for melody in melodies:
            notes = melody.split()
            for i in range(len(notes) - 1):
                current_note = notes[i]
                next_note = notes[i+1]
                
                if current_note not in self.chain:
                    self.chain[current_note] = []
                self.chain[current_note].append(next_note)
                
    def compose(self, start_note=None, length=16):
        """
        Generates a new melody based on the learned chain.
        """
        if not self.chain:
            return ""
            
        # Pick a random starting note if none provided or if invalid
        if start_note not in self.chain:
            start_note = random.choice(list(self.chain.keys()))
            
        melody = [start_note]
        current_note = start_note
        
        for _ in range(length - 1):
            if current_note in self.chain:
                next_note = random.choice(self.chain[current_note])
                melody.append(next_note)
                current_note = next_note
            else:
                # Dead end in chain, pick random restart
                current_note = random.choice(list(self.chain.keys()))
                melody.append(current_note)
                
        return " ".join(melody)
