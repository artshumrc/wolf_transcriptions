def is_timestamp(text: str) -> bool:
    """Check if string starts with timestamp pattern like '1:10:37' or '10:30' or '[00:00:22:01]'"""

    if not text or ":" not in text:
        return False
    
    if text.startswith('[') and text.endswith(']'):
        text = text[1:-1]
    
    parts = text.split(":")
    
    last_part = parts[-1]
    if "." in last_part:
        decimal_parts = last_part.split(".")
        if len(decimal_parts) != 2:
            return False
        
        if not decimal_parts[0].isnumeric() or not decimal_parts[1].isnumeric():
            return False
            
        # delete the milliseconds decimal for final checks
        parts.pop(-1)
    
    for part in parts:
        if not part.isnumeric():
            return False
            
    # Valid timestamp should have 2-4 parts
    return 2 <= len(parts) <= 4

def add_header(metadata, webvtt):
    if not metadata:
        return webvtt
    webvtt.append("NOTE")
    webvtt.extend(metadata)
    webvtt.append("\n")
    return webvtt

def convert_timestamp_to_webvtt(timestamp: str, framerate: int = 30, add_seconds: int = 0):
        
    # Handle decimal point format (e.g., 00:00:22.01)
    if "." in timestamp:
        base_timestamp, fraction = timestamp.rsplit(".", 1)
        parts = base_timestamp.split(":")
        
        # Convert seconds part to milliseconds (ensuring it's 3 digits)
        milliseconds = int(fraction.ljust(3, '0')[:3])
        
        if len(parts) == 2:  # MM:SS.ms
            minutes = int(parts[0])
            seconds = int(parts[1]) + add_seconds
            return f"00:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        elif len(parts) == 3:  # HH:MM:SS.ms
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2]) + add_seconds
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    parts = timestamp.split(":")
    
    # Handle frame-based timestamp (HH:MM:SS:FF)
    if len(parts) == 4:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2]) + add_seconds
        frames = int(parts[3])
        
        # Convert frames to milliseconds based on framerate
        milliseconds = int((frames / framerate) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    # Standard timestamp without frames
    if len(parts) == 2:  # MM:SS
        minutes = int(parts[0])
        seconds = int(parts[1]) + add_seconds
        return f"00:{minutes:02d}:{seconds:02d}.000"
    elif len(parts) == 3:  # HH:MM:SS
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2]) + add_seconds
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.000"
    
    # fallback
    return f"{timestamp}.000"

def update_cue(cue, webvtt, line, framerate=30):
    parts = line.split()
    if not parts:
        return webvtt, cue
        
    timestamp = parts[0]
    if not is_timestamp(timestamp):
        cue["lines"].append(line.strip())
        return webvtt, cue
    
    # Strip square brackets if present
    if timestamp.startswith('[') and timestamp.endswith(']'):
        actual_timestamp = timestamp[1:-1]
    else:
        actual_timestamp = timestamp
    line = line.replace(timestamp, "", 1).strip()
    
    if not cue["start"]: # first cue
        cue["start"] = actual_timestamp
        if line:  # Only add if line is not empty
            cue["lines"].append(line)
    elif not cue["end"]:
        cue["end"] = actual_timestamp
        if line:  # Only add if line is not empty
            cue["lines"].append(line)
        # Add completed cue
        start_vtt = convert_timestamp_to_webvtt(cue['start'], framerate)
        end_vtt = convert_timestamp_to_webvtt(cue['end'], framerate)
        webvtt.append(f"{start_vtt} --> {end_vtt}")
        webvtt.extend(cue["lines"])
        webvtt.append("")
        # Start new cue with same timestamp
        cue["start"] = actual_timestamp
        cue["end"] = ""
        cue["lines"] = []
        if line:  # Only add if line is not empty
            cue["lines"].append(line)
    else: # new cue, add the old one
        start_vtt = convert_timestamp_to_webvtt(cue['start'], framerate)
        end_vtt = convert_timestamp_to_webvtt(cue['end'], framerate)
        webvtt.append(f"{start_vtt} --> {end_vtt}")
        webvtt.extend(cue["lines"])
        webvtt.append("")
        # reset the cue
        cue["start"] = actual_timestamp
        cue["end"] = ""
        cue["lines"] = [line]
    return webvtt, cue

def wolf_to_webvtt(text: str, recording_length: str|None, framerate: float|None):
    if not recording_length or not recording_length.strip():
        recording_length = None
    else:
        recording_length = recording_length.strip()
    if not isinstance(framerate, (int, float)):
        framerate = 30
    
    hit_first_timestamp = False
    current_cue = {"start": "", "end": "", "lines": []}
    metadata = []
    webvtt = ["WEBVTT", "\n"]
    
    for line in text.splitlines():
        if not line.strip():
            continue
            
        parts = line.split()
        if parts and is_timestamp(parts[0]) and not hit_first_timestamp:
            hit_first_timestamp = True
            webvtt = add_header(metadata, webvtt)
            webvtt, current_cue = update_cue(current_cue, webvtt, line, framerate)
        elif hit_first_timestamp:
            webvtt, current_cue = update_cue(current_cue, webvtt, line, framerate)
        else:
            metadata.append(line.strip())
    
    # Add the last cue if it exists
    if current_cue["start"] and current_cue["lines"]:
        if not current_cue["end"]:
            if recording_length and is_timestamp(recording_length):
                # Use recording length as the end time for the last cue
                current_cue["end"] = recording_length
            else:
                current_cue["end"] = current_cue["start"]  # Will be modified by add_seconds parameter
        
        start_vtt = convert_timestamp_to_webvtt(current_cue['start'], framerate)
        if current_cue["end"] == current_cue["start"]:  # We need to arbitrarily add seconds
            end_vtt = convert_timestamp_to_webvtt(current_cue['start'], framerate, 3)
        else:
            end_vtt = convert_timestamp_to_webvtt(current_cue['end'], framerate)
            
        webvtt.append(f"{start_vtt} --> {end_vtt}")
        webvtt.extend(current_cue["lines"])
        
    return webvtt
