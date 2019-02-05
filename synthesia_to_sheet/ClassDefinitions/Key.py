import Color
import Note

class Key():
    """docstring for Key."""
    def __init__(self, color, location, nativeColor, note=None, octave=None, isPressed=False, duration=None):
        self.Color = color
        self.Note = note
        self.NativeColor = nativeColor # useful to compare against when the key is pressed
        self.Octave = octave
        self.Location = location
        self.IsPressed = isPressed
        self.Duration = duration

    def is_left_of(self, key):
        return self.Location[0] < key.Location[0]

    def is_right_of(self, key):
        return self.Location[0] > key.Location[0]
