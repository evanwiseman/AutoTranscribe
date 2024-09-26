from spleeter.separator import Separator
import librosa
import music21 as m21
from midiutil import MIDIFile
from multiprocessing import freeze_support
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Function to separate audio tracks using Spleeter
def separate_tracks(audio_file):
    separator = Separator('spleeter:5stems')
    output_dir = './output'
    separator.separate_to_file(audio_file, output_dir)
    return output_dir  # Return the directory with the separated tracks

# Function to transcribe audio to MIDI
def transcribe_to_midi(audio_file, output_midi_file):
    # Load audio file
    y, sr = librosa.load(audio_file)

    # Use librosa to extract pitches
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)

    # Initialize a MIDI file
    midi = MIDIFile(1)
    midi.addTempo(0, 0, 120)

    note_count = 0  # Counter to keep track of detected notes

    # Extract note information and add to MIDI
    for t in range(pitches.shape[1]):
        pitch = pitches[:, t].max()  # Get the max pitch at time t
        if pitch > 0:
            note_midi = int(librosa.hz_to_midi(pitch))
            midi.addNote(0, 0, note_midi, t, 1, 100)
            note_count += 1

    if note_count == 0:
        print(f"No notes detected in {audio_file}. Skipping MIDI creation.")
        return  # Don't attempt to write MIDI if no notes are found

    # Save the MIDI file
    with open(output_midi_file, 'wb') as midi_file:
        midi.writeFile(midi_file)
    print(f"MIDI file saved: {output_midi_file}")


# Function to convert MusicXML to PDF
def convert_musicxml_to_pdf(musicxml_file, pdf_file):
    # Load the music21 stream from MusicXML
    score = m21.converter.parse(musicxml_file)

    # Create a PDF canvas
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter

    # Draw notes on the PDF
    for element in score.flat.notes:
        if element.isNote:
            # Example: Draw notes in a vertical line
            c.drawString(100, height - (element.pitch.midi * 5), str(element.pitch))  # Example positioning
        elif element.isChord:
            for note in element.notes:
                c.drawString(100, height - (note.pitch.midi * 5), str(note.pitch))  # Example positioning

    c.save()
    print(f"PDF file saved: {pdf_file}")

# Function to transcribe audio to sheet music (MusicXML format)
def transcribe_to_sheet_music(audio_file, output_sheet_music_file):
    # Load the audio file
    y, sr = librosa.load(audio_file)

    # Use librosa to extract pitches
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)

    # Initialize a music21 stream
    stream = m21.stream.Stream()

    # Extract note information and add to the stream
    for t in range(pitches.shape[1]):
        pitch = pitches[:, t].max()  # Get the max pitch
        if pitch > 0:
            note = m21.note.Note(librosa.hz_to_midi(pitch))
            stream.append(note)

    # Save the stream as MusicXML (sheet music)
    stream.write('musicxml', fp=output_sheet_music_file)
    pdf_file = output_sheet_music_file.replace(".xml", ".pdf")
    convert_musicxml_to_pdf(output_sheet_music_file, pdf_file)
    
    

# Main function to process the song, separate tracks, and transcribe them
def process_song(audio_file):
    # Step 1: Separate the tracks
    output_dir = separate_tracks(audio_file)
    
    # Step 2: Transcribe each track to MIDI and sheet music
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".wav"):
                track_path = os.path.join(root, file)
                midi_path = track_path.replace(".wav", ".midi")
                sheet_music_path = track_path.replace(".wav", ".xml")
                # Transcribe each track
                midi_output = f"{midi_path}.midi"
                sheet_music_output = f"{sheet_music_path}.xml"

                print(f"Transcribing {track_path} to MIDI and sheet music...")

                transcribe_to_midi(track_path, midi_output)
                transcribe_to_sheet_music(track_path, sheet_music_output)

                print(f"MIDI and sheet music saved for {file}.")

# Entry point of the program
if __name__ == '__main__':
    freeze_support()  # Needed for Windows multiprocessing

    # Path to the audio file to process
    audio_file = 'shelter.mp3'  # Replace with actual path

    # Process the song: separate and transcribe
    process_song(audio_file)
