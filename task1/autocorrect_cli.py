# autocorrect_cli.py
# A simple autocorrect demo using pyspellchecker

import re
from spellchecker import SpellChecker

# Initialize spellchecker
spell = SpellChecker()

# Regex to split words & punctuation
PUNCT_TOKENIZER = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def preserve_case(original: str, corrected: str) -> str:
    """Preserve case when replacing a word"""
    if original.isupper():
        return corrected.upper()
    if original.istitle():
        return corrected.capitalize()
    return corrected


def should_ignore(word: str) -> bool:
    """Skip very short words, acronyms, or words with digits"""
    return len(word) < 3 or any(ch.isdigit() for ch in word) or word.isupper()


def correct_text(text: str, mode: str = "suggest"):
    """
    Correct text by detecting misspellings.
    mode = "suggest" → show suggestions only
    mode = "auto" → automatically replace with best match
    """
    tokens = PUNCT_TOKENIZER.findall(text)
    output_tokens = []
    report = []  # stores (wrong_word, suggestions)

    for tok in tokens:
        if tok.isalpha() and not should_ignore(tok):
            lower = tok.lower()
            if lower in spell:  # already correct
                output_tokens.append(tok)
            else:
                # generate corrections
                top = spell.correction(lower)
                candidates = list(spell.candidates(lower))
                suggestions = [top] + [c for c in candidates if c != top]
                suggestions = suggestions[:3]

                report.append((tok, suggestions))

                if mode == "auto" and top:
                    output_tokens.append(preserve_case(tok, top))
                else:
                    output_tokens.append(tok)  # keep as-is
        else:
            output_tokens.append(tok)

    # rebuild text with spacing rules
    output_text = ""
    for tok in output_tokens:
        if tok.isalnum():  # word
            output_text += tok + " "
        else:  # punctuation
            output_text = output_text.rstrip() + tok + " "

    return output_text.strip(), report


if __name__ == "__main__":
    sample = "Ths is a smple sentnce with teh erors."
    corrected, findings = correct_text(sample, mode="auto")

    print("Input   :", sample)
    print("Output  :", corrected)
    print("Flagged :")
    for wrong, suggs in findings:
        print(f"  {wrong} -> {', '.join(suggs)}")
