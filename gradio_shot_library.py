# Shot Types
SHOT_TYPES = {
    "Extreme Wide Shot (EWS)": "Shows a broad view of the surroundings around the character, often used as an establishing shot.",
    "Very Wide Shot (VWS)": "Encompasses a wide view but closer than an extreme wide shot.",
    "Wide Shot (WS)": "Shows the full character from head to toe, with some surroundings visible.",
    "Mid Shot (MS)": "Shows a character from the waist up.",
    "Medium Close-Up (MCU)": "Shows a character from the chest up.",
    "Close-Up (CU)": "Tightly frames a character's face.",
    "Extreme Close-Up (ECU)": "Shows extreme detail, such as a single facial feature.",
    "Two Shot": "Frames two characters in the same shot.",
    "Over-the-Shoulder (OTS)": "Shows a character from behind the shoulder of another character.",
    "Point of View (POV)": "Shows the scene from a character's perspective.",
    "Insert Shot": "A close-up of an object or detail that's significant to the story.",
    "Cutaway": "A shot of something other than the main action, often used to add context or information.",
    "Reaction Shot": "Shows a character's reaction to something on or off-screen.",
}

# Camera Angles
CAMERA_ANGLES = {
    "Eye Level": "Camera is positioned at the subject's eye level, creating a neutral perspective.",
    "Low Angle": "Camera looks up at the subject, making them appear more powerful or dominant.",
    "High Angle": "Camera looks down at the subject, making them appear smaller or vulnerable.",
    "Dutch Angle": "Camera is tilted to one side, creating a sense of unease or disorientation.",
    "Bird's Eye View": "Camera looks directly down on the scene from above.",
    "Worm's Eye View": "Camera looks up from ground level.",
    "Three-Quarter View": "Subject is at a 45-degree angle to the camera, showing more depth.",
    "Profile": "Subject is viewed from the side.",
    "Front View": "Subject is viewed directly from the front.",
    "Rear View": "Subject is viewed from behind.",
}

# Camera Movements
CAMERA_MOVEMENTS = {
    "Static": "Camera remains still.",
    "Pan": "Camera rotates horizontally while remaining in a fixed position.",
    "Tilt": "Camera rotates vertically while remaining in a fixed position.",
    "Zoom": "Lens is adjusted to change the focal length, appearing to move closer to or further from the subject.",
    "Dolly": "Camera moves towards or away from the subject.",
    "Truck": "Camera moves horizontally, parallel to the subject.",
    "Pedestal": "Camera moves vertically up or down.",
    "Crane": "Camera is mounted on a crane or jib, allowing for complex, sweeping movements.",
    "Handheld": "Camera is operated without a stabilizing device, creating a more dynamic, sometimes shaky image.",
    "Steadicam": "Camera is mounted on a stabilizing device worn by the operator, allowing for smooth movement.",
    "Tracking": "Camera follows a moving subject, maintaining a consistent distance.",
}

# Framing
FRAMING = {
    "Centered": "Subject is positioned in the center of the frame.",
    "Rule of Thirds": "Subject is positioned at the intersection of imaginary lines that divide the frame into thirds.",
    "Balanced": "Elements in the frame are distributed evenly, creating a sense of stability.",
    "Unbalanced": "Elements are distributed unevenly, creating tension or drawing attention to a specific area.",
    "Leading Lines": "Lines in the composition guide the viewer's eye to the main subject.",
    "Framing within the Frame": "Using elements within the scene to create a frame around the subject.",
    "Symmetry": "Elements are arranged symmetrically, creating a sense of order and balance.",
    "Asymmetry": "Elements are arranged asymmetrically, creating visual interest and tension.",
}

# Depth of Field
DEPTH_OF_FIELD = {
    "Deep Focus": "Everything in the frame is in sharp focus.",
    "Shallow Focus": "Subject is in focus while the background is blurred.",
    "Rack Focus": "Focus changes from one subject to another within the shot.",
}

def get_all_options():
    return {
        "Shot Types": list(SHOT_TYPES.keys()),
        "Camera Angles": list(CAMERA_ANGLES.keys()),
        "Camera Movements": list(CAMERA_MOVEMENTS.keys()),
        "Framing": list(FRAMING.keys()),
        "Depth of Field": list(DEPTH_OF_FIELD.keys()),
    }

def get_description(category, option):
    if category == "Shot Types":
        return SHOT_TYPES.get(option, "")
    elif category == "Camera Angles":
        return CAMERA_ANGLES.get(option, "")
    elif category == "Camera Movements":
        return CAMERA_MOVEMENTS.get(option, "")
    elif category == "Framing":
        return FRAMING.get(option, "")
    elif category == "Depth of Field":
        return DEPTH_OF_FIELD.get(option, "")
    else:
        return ""
