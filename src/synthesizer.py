
import numpy as np
from scipy.io.wavfile import write
from scipy import signal

class Synthesizer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        # Basic frequencies for the 4th octave (A4 = 440Hz)
        self.note_freqs = {
            'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
            'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
            'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
        }

    def get_frequency(self, note_str):
        """
        Parses a note string like 'C4', 'A#5', 'Gb3' into frequency.
        Defaults to octave 4 if not specified.
        """
        note_str = note_str.upper()
        if not note_str:
            return 0.0
            
        # Handle simple flat/sharp conversion
        if note_str[-1].isdigit():
            octave = int(note_str[-1])
            note = note_str[:-1]
        else:
            octave = 4
            note = note_str
            
        base_freq = self.note_freqs.get(note)
        if base_freq is None:
            print(f"Warning: Note {note} not found, skipping.")
            return 0.0
            
        return base_freq * (2 ** (octave - 4))

    def generate_wave(self, frequency, duration_sec, wave_type='sine'):
        t = np.linspace(0, duration_sec, int(self.sample_rate * duration_sec), False)
        
        if wave_type == 'sine':
            return np.sin(frequency * t * 2 * np.pi)
        elif wave_type == 'square':
            return signal.square(frequency * t * 2 * np.pi)
        elif wave_type == 'sawtooth':
            return signal.sawtooth(frequency * t * 2 * np.pi)
        else:
            return np.sin(frequency * t * 2 * np.pi)

    def apply_envelope(self, wave, duration_sec):
        # Basic ADSR: 10% Attack, 10% Decay, 50% Sustain Level, 20% Release
        total_samples = len(wave)
        attack_len = int(0.1 * total_samples)
        decay_len = int(0.1 * total_samples)
        release_len = int(0.2 * total_samples)
        sustain_len = total_samples - attack_len - decay_len - release_len
        
        sustain_level = 0.7
        
        attack = np.linspace(0, 1, attack_len)
        decay = np.linspace(1, sustain_level, decay_len)
        sustain = np.full(sustain_len, sustain_level)
        release = np.linspace(sustain_level, 0, release_len)
        
        envelope = np.concatenate([attack, decay, sustain, release])
        
        # Handle potential length mismatch due to rounding
        if len(envelope) < total_samples:
            envelope = np.pad(envelope, (0, total_samples - len(envelope)), 'constant')
        elif len(envelope) > total_samples:
            envelope = envelope[:total_samples]
            
        return wave * envelope

    def generate_audio(self, note_sequence, bpm=120, wave_type='sine'):
        audio_data = []
        
        notes = note_sequence.split()
        
        # 60 seconds / BPM = duration of one beat (quarter note)
        beat_duration = 60.0 / bpm
        
        for token in notes:
            # Parse token "Note:Duration" (e.g., "C4:1", "D#5:0.5")
            if ':' in token:
                note_str, duration_str = token.split(':')
                try:
                    duration_multiplier = float(duration_str)
                except ValueError:
                    duration_multiplier = 1.0
            else:
                note_str = token
                duration_multiplier = 1.0 # Default to 1 beat
            
            # Allow "R" or "REST" for silence
            if note_str.upper() in ["R", "REST"]:
                freq = 0.0
            else:
                freq = self.get_frequency(note_str)
            
            duration_sec = beat_duration * duration_multiplier
            
            if freq > 0:
                wave = self.generate_wave(freq, duration_sec, wave_type)
                wave = self.apply_envelope(wave, duration_sec)
                audio_data.append(wave)
            else:
                # Insert silence for rests
                silence = np.zeros(int(self.sample_rate * duration_sec))
                audio_data.append(silence)
                
            # Add a tiny bit of silence/spacing (can be removed if we want legato)
            # reduced to very small amount or zero if we trust envelope
            gap = np.zeros(int(self.sample_rate * 0.01)) 
            audio_data.append(gap)
            
        if not audio_data:
            return None
            
        combined_signal = np.concatenate(audio_data)
        
        # Normalize to 16-bit range
        if np.max(np.abs(combined_signal)) > 0:
             combined_signal *= 32767 / np.max(np.abs(combined_signal))
             
        return combined_signal.astype(np.int16)

    def save_wav(self, filename, data):
        write(filename, self.sample_rate, data)
        print(f"Saved to {filename}")
