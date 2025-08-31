# autocorrect_gui.py
# A simple real-time autocorrect demo with Tkinter

import re
import tkinter as tk
from tkinter import ttk
from spellchecker import SpellChecker

# Initialize spellchecker
spell = SpellChecker()

# Regex to detect words
WORD_RE = re.compile(r"[A-Za-z]+$")
# Keys or characters that trigger correction
END_TRIGGERS = ("space", "Return", ".", ",", "!", "?", ";", ":")


def preserve_case(original: str, corrected: str) -> str:
    """Preserve the original word's casing when replacing."""
    if original.isupper():
        return corrected.upper()
    if original.istitle():
        return corrected.capitalize()
    return corrected


def should_ignore(word: str) -> bool:
    """Ignore very short words, acronyms, or words with digits."""
    return len(word) < 3 or any(ch.isdigit() for ch in word) or word.isupper()


def get_last_word(text_widget: tk.Text):
    """Find the last word before the cursor in the Text widget."""
    end_idx = text_widget.index("insert")
    before = text_widget.get("1.0", end_idx)

    # Match the last word
    match = re.search(r"([A-Za-z]+)\W*$", before)
    if not match:
        return None, None, None

    word = match.group(1)

    # Find the start index of the word
    start_idx = text_widget.search(r"\m" + word + r"\M", end_idx,
                                   stopindex="1.0", regexp=True, backwards=True)
    if not start_idx:
        return None, None, None

    start_line, start_col = map(int, start_idx.split("."))
    end_col = start_col + len(word)
    end_idx = f"{start_line}.{end_col}"
    return word, start_idx, end_idx


def suggest_for(word: str):
    """Return top 3 correction suggestions for a word."""
    lower = word.lower()
    top = spell.correction(lower)
    candidates = list(spell.candidates(lower))
    ordered = [top] + [c for c in candidates if c != top]
    return ordered[:3]


class AutoCorrectApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Autocorrect Keyboard Demo")
        self.geometry("800x400")

        self.auto_var = tk.BooleanVar(value=True)

        # Text box
        self.text = tk.Text(self, wrap="word", font=(
            "Segoe UI", 12), undo=True)
        self.text.pack(fill="both", expand=True, padx=12, pady=(12, 6))

        # Options bar
        options = ttk.Frame(self)
        options.pack(fill="x", padx=12, pady=(0, 6))
        ttk.Checkbutton(options, text="Auto-replace",
                        variable=self.auto_var).pack(side="left")

        # Suggestion label
        self.sugg_label = ttk.Label(self, text="Suggestions: ", anchor="w")
        self.sugg_label.pack(fill="x", padx=12, pady=(0, 12))

        # Bind key release
        self.text.bind("<KeyRelease>", self.on_key_release)

    def on_key_release(self, event):
        """Triggered when a key is released."""
        if event.keysym not in END_TRIGGERS and event.char not in END_TRIGGERS:
            # Update suggestions while typing
            self.update_suggestions_live()
            return

        word_info = get_last_word(self.text)
        if not word_info:
            self.sugg_label.config(text="Suggestions: ")
            return

        word, start_idx, end_idx = word_info
        if not word or should_ignore(word):
            self.sugg_label.config(text="Suggestions: ")
            return

        if word.lower() in spell:
            self.sugg_label.config(text="Suggestions: ")
            return

        suggestions = suggest_for(word)
        if self.auto_var.get() and suggestions:
            fixed = preserve_case(word, suggestions[0])
            # Replace word in text
            self.text.delete(start_idx, end_idx)
            self.text.insert(start_idx, fixed)
            self.sugg_label.config(
                text=f"Suggestions: {', '.join(suggestions)} (auto → {suggestions[0]})")
        else:
            self.sugg_label.config(
                text=f"Suggestions: {', '.join(suggestions)}")

    def update_suggestions_live(self):
        """Update suggestions while user is typing."""
        word_info = get_last_word(self.text)
        if not word_info:
            self.sugg_label.config(text="Suggestions: ")
            return

        word, _, _ = word_info
        if not word or should_ignore(word) or word.lower() in spell:
            self.sugg_label.config(text="Suggestions: ")
            return

        suggestions = suggest_for(word)
        self.sugg_label.config(text=f"Suggestions: {', '.join(suggestions)}")


if __name__ == "__main__":
    app = AutoCorrectApp()
    app.mainloop()
