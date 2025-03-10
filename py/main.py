import sys
import js

sys.path.append("py")
import converter

def convert_text(text: str, recording_length: str, framerate: str) -> str:
    # validate inputs
    recording_length = recording_length.strip()
    framerate = framerate.strip()
    text = text.strip()
    if not text:
        return "Please paste some text to convert."
    if not recording_length:
        recording_length = None
    if not framerate:
        framerate = None
    else:
        try:
            framerate = float(framerate)
        except ValueError:
            return "Invalid framerate. Please enter a valid number."
    
    
    webvtt_lines = converter.wolf_to_webvtt(text, recording_length, framerate)
    return "\n".join(webvtt_lines)
    
# Make the function available to JavaScript
js.window.pyConvertToWebVtt = convert_text