import Colour
import Note

class Key():
    """docstring for Key."""
    def __init__(self, colour, location, nativeColor, note=None, octave=None, isPressed=None, duration=None):
        self.Colour = colour
        self.Note = note
        self.NativeColor = nativeColor # useful to compare against when the key is pressed
        self.Octave = octave
        self.Location = location
        self.IsPressed = isPressed
        self.Duration = duration
