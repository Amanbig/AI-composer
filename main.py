
from synthesizer import Synthesizer
from composer import MarkovComposer
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Music Generation System")
    parser.add_argument("notes", nargs="*", help="String of notes (e.g. 'C4 E4 G4')")
    parser.add_argument("--wave", choices=['sine', 'square', 'sawtooth'], default='sine', help="Waveform type")
    parser.add_argument("--compose", action="store_true", help="Generate a melody using AI")
    
    args = parser.parse_args()
    
    synth = Synthesizer()
    composer = MarkovComposer()
    
    print("Music Generation System Initialized")
    
    if args.compose:
        print("Training AI Composer...")
        data = composer.load_data()
        composer.train(data)
        input_string = composer.compose(length=20)
        print(f"AI Composed: {input_string}")
    elif args.notes:
        input_string = " ".join(args.notes)
    else:
        print("Enter a string of notes (e.g., 'C4 D4 E4'):")
        input_string = input(">> ")
        
    print(f"Generating audio for: {input_string} using {args.wave} wave")
    
    audio_data = synth.generate_audio(input_string, wave_type=args.wave)
    
    if audio_data is not None:
        output_file = "output.wav"
        synth.save_wav(output_file, audio_data)
        print("Done!")
    else:
        print("No valid notes found to generate audio.")

if __name__ == "__main__":
    main()
