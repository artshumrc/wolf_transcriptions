def is_timestamp(text):
    """Check if string starts with timestamp pattern like '1:10:37' or '10:30'"""
    if not text or ":" not in text:
        return False
    if not text.replace(":", "").isnumeric():
        return False
    return True

def add_header(metadata, webvtt):
    if not metadata:
        return webvtt
    webvtt.append("NOTE")
    webvtt.extend(metadata)
    webvtt.append("\n")
    return webvtt

def update_cue(cue, webvtt, line):
    parts = line.split()
    if not parts:
        return webvtt, cue
        
    timestamp = parts[0]
    if not is_timestamp(timestamp):
        cue["lines"].append(line.strip())
        return webvtt, cue
    
    line = line.replace(timestamp, "", 1).strip()
    cue["lines"].append(line)
    if not cue["start"]: # first cue
        cue["start"] = timestamp
    elif not cue["end"]:
        cue["end"] = timestamp
    else: # new cue, add the old one
        webvtt.append(f"{cue['start']}.000 --> {cue['end']}.000")
        webvtt.extend(cue["lines"])
        webvtt.append("")
        # reset the cue
        cue["start"] = timestamp
        cue["end"] = ""
        cue["lines"] = [line]
    return webvtt, cue

def wolf_to_webvtt(text):
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
            webvtt, current_cue = update_cue(current_cue, webvtt, line)
        elif hit_first_timestamp:
            webvtt, current_cue = update_cue(current_cue, webvtt, line)
        else:
            metadata.append(line.strip())

    # Add the last cue if it exists
    if current_cue["start"] and current_cue["lines"]:
        if not current_cue["end"]:
            # Estimate end time if not provided
            try:
                start_min_hr, start_second = current_cue["start"].rsplit(":", 1)
                end_second = int(start_second) + 3
                end_timestamp = f"{start_min_hr}:{end_second:02d}"
                current_cue["end"] = end_timestamp
            except Exception:
                # If something goes wrong with time calculation, use start time + 3 sec
                current_cue["end"] = current_cue["start"] 
        
        webvtt.append(f"{current_cue['start']}.000 --> {current_cue['end']}.000")
        webvtt.extend(current_cue["lines"])
        
    return webvtt
