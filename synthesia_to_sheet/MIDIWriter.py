from midiutil import MIDIFile
from ClassDefinitions import Key

class MIDIWriter(MIDIFile):
    """docstring for MIDIWriter."""
    def __init__(self, tempo=60, volume=100):
        super(MIDIWriter, self).__init__()
        self.Track = 0
        self.Channel = 0
        self.Time = 0
        self.Tempo = tempo
        self.Volume = volume
        self.middleCNoteMIDI = 60
        self.addTempo(self.Track, self.Time, self.Tempo)

    # Add the return value of this to the key index (of Piano.keys) to get the MIDI note number
    def addend_to_get_midi_note(middleCIndex):
        return self.middleCNoteMIDI - middleCIndex

    # Given a list of keyPresses(tuple of list of keys pressed and duration of the press) for a frame, adds the notes to MIDI
    def add_notes_to_midi(self, keyPresses):
        for keyPress, duration in keyPresses:
            for key in keyPress:
                self.addNote(self.Track, self.Channel, key, self.Time, duration, self.Volume)
            self.Time = self.Time + duration

    # Once all the notes are added to the MIDIWriter, create a MIDI output file
    def write_midi_to_file(self):
        with open("my_output.mid", "wb") as output_file:
            self.writeFile(output_file)
