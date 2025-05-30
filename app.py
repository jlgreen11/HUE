
import streamlit as st
import json, numpy as np
from colorsys import rgb_to_hsv
from math import sqrt

# --- load board --------------------------------------------------------------
with open('board_colors.json') as f:
    board_rgb = np.array(json.load(f))         # shape (30,16,3)
rows, cols, _ = board_rgb.shape

def rgb2lab(rgb):
    # quick & dirty linearised conversion, good enough for distance sorting
    r, g, b = [x/255.0 for x in rgb]
    return np.array([r*100, g*100, b*100])

lab_board = np.apply_along_axis(rgb2lab, 2, board_rgb)
flat_lab = lab_board.reshape(-1,3)

# index helpers ---------------------------------------------------------------
def idx_to_coord(idx):
    r = idx // cols
    c = idx % cols
    return chr(65+c), rows - r   # A‑P, 30‑1 (matches board)

def best_match(color_lab):
    dists = np.linalg.norm(flat_lab - color_lab, axis=1)
    idx = int(np.argmin(dists))
    return idx_to_coord(idx), dists[idx]

# --- naive phrase→RGB heuristic ---------------------------------------------
BASIC = {
    "red":     (220, 20, 60),
    "orange":  (255, 140, 0),
    "yellow":  (255, 215, 0),
    "green":   (34, 139, 34),
    "blue":    (65,105,225),
    "purple":  (128,0,128),
    "pink":    (255,105,180),
    "brown":   (139,69,19),
    "gray":    (119,136,153),
    "black":   (0,0,0),
    "white":   (245,245,245),
}

import json, re
with open("xkcd_colors.json") as f:
    XKCD = json.load(f)  # dict: name → "#rrggbb"

def phrase_to_rgb(phrase):
    phrase = phrase.lower()
    for name, hexcode in XKCD.items():
        if re.search(rf"\\b{name}\\b", phrase):
            r = int(hexcode[1:3], 16)
            g = int(hexcode[3:5], 16)
            b = int(hexcode[5:7], 16)
            return (r, g, b)
    # descriptor tweaks (dark/light) handled below…
    return (127, 127, 127)  # fallback


# ---------------------------------------------------------------------------
st.title("Hues & Cues Helper")

st.markdown(
"""Type the clue the Cue‑giver just said.  
The app returns the **best‑guess square** (column‑letter, row‑number) after each clue.  
Add the second clue to refine the pick and hit *Guess* again.""")

clue1 = st.text_input("First clue (one‑word/phrase):")
clue2 = st.text_input("Second clue (optional):")

if st.button("Guess"):
    if not clue1:
        st.warning("Enter at least the first clue.")
    else:
        # combine clues: weight 70/30 first vs second
        rgb1 = phrase_to_rgb(clue1)
        lab1 = rgb2lab(rgb1)
        if clue2:
            rgb2 = phrase_to_rgb(clue2)
            lab2 = rgb2lab(rgb2)
            combined = (0.7*lab1 + 0.3*lab2)
        else:
            combined = lab1
        (col, row), dist = best_match(combined)
        st.success(f"Try **{col}{row}**  (distance score ≈ {dist:.1f})")
        st.caption("Column letter (A‑P) & row number (1‑30). \nSmaller distance = closer match.")

st.divider()
st.markdown("ℹ️ *Prototype logic: BASIC dictionary & simple brightness modifiers. Feel free to expand!*")
