import sys
import js

sys.path.append("py")
import converter

def convert_text(text):
    if not text.strip():
        return "Please paste some text to convert."
    
    webvtt_lines = converter.wolf_to_webvtt(text)
    return "\n".join(webvtt_lines)
    
# Make the function available to JavaScript
js.window.pyConvertToWebVtt = convert_text