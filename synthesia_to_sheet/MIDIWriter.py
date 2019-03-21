from midiutil import MIDIFile
from ClassDefinitions import Key
from ClassDefinitions import Hand
import numpy as np
from sklearn.cluster import KMeans

class MIDIWriter(MIDIFile):
    """docstring for MIDIWriter."""
    def __init__(self, tempo=60, volume=100):
        super(MIDIWriter, self).__init__(numTracks=2)
        self.Channel = 0
        self.Time = 0
        self.Tempo = tempo
        self.Volume = volume
        self.middleCNoteMIDI = 60
        self.addTempo(Hand.Hand.Left.value-1, self.Time, self.Tempo)
        self.addTempo(Hand.Hand.Right.value-1, self.Time, self.Tempo)
        self.durations = []

    # Add the return value of this to the key index (of Piano.keys) to get the MIDI note number
    def addend_to_get_midi_note(self, middleCIndex):
        return self.middleCNoteMIDI - middleCIndex

    def record_key_presses(self, keys, offset, hand):
        for i, key in enumerate(keys):
            if len(key.Presses) > 0 :
                self.add_notes_to_midi(i+offset, key.Presses, hand)

    # Given a list of keyPresses(tuple of list of keys pressed and duration of the press) for a frame, adds the notes to MIDI
    def add_notes_to_midi(self, key, keyPresses, hand):
        for press in keyPresses:
            if press[0] == hand and press[1] < press[2]:
                self.durations.append(press[2] - press[1])
                self.addNote(hand.value-1, self.Channel, key, press[1], press[2] - press[1], self.Volume)

    # Once all the notes are added to the MIDIWriter, create a MIDI output file
    def write_midi_to_file(self):
        with open("my_output.mid", "wb") as output_file:
            self.writeFile(output_file)
