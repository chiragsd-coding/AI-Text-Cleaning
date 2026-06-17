"""
Text Cleaning Service
Provides comprehensive text cleaning and autocorrection across 8 operations.
"""
import re
import html
from typing import Dict, List, Optional
import emoji
import ftfy
from better_profanity import profanity
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


class TextCleaner:
    """Main text cleaning service with all 8 operations."""

    def __init__(self):
        """Initialize all cleaning tools."""
        # Load profanity filter
        # profanity.load_default_wordlist()

        # Initialize Presidio for PII detection
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def clean(
        self,
        text: str,
        operations: Optional[List[str]] = None,
        target_style: str = "formal",
    ) -> Dict:
        """
        Main cleaning method. Applies selected operations in sequence.

        Args:
            text: Input text to clean
            operations: List of operations to apply. If None, applies all.
                       Valid: ['grammar', 'spaces', 'capitalization', 'emojis',
                              'profanity', 'pii', 'ocr', 'style']
            target_style: Target style for text conversion
                         (formal, casual, technical, simple)

        Returns:
            Dict with cleaned_text and metadata about operations applied
        """
        if not operations:
            operations = [
                "grammar",
                "spaces",
                "capitalization",
                "emojis",
                "profanity",
                "pii",
                "ocr",
                "style",
            ]

        result = {
            "original_text": text,
            "cleaned_text": text,
            "operations_applied": [],
            "metadata": {
                "original_length": len(text),
                "cleaned_length": 0,
                "changes_made": {},
            },
        }

        # Track original for comparison
        current_text = text

        # Apply each operation
        for op in operations:
            if op == "grammar":
                current_text, changes = self._fix_grammar(current_text)
                result["operations_applied"].append("grammar")
                result["metadata"]["changes_made"]["grammar"] = changes
            elif op == "spaces":
                current_text, changes = self._fix_extra_spaces(current_text)
                result["operations_applied"].append("spaces")
                result["metadata"]["changes_made"]["spaces"] = changes
            elif op == "capitalization":
                current_text, changes = self._standardize_capitalization(
                    current_text
                )
                result["operations_applied"].append("capitalization")
                result["metadata"]["changes_made"]["capitalization"] = changes
            elif op == "emojis":
                current_text, changes = self._remove_emojis(current_text)
                result["operations_applied"].append("emojis")
                result["metadata"]["changes_made"]["emojis"] = changes
            elif op == "profanity":
                current_text, changes = self._clean_profanity(current_text)
                result["operations_applied"].append("profanity")
                result["metadata"]["changes_made"]["profanity"] = changes
            elif op == "pii":
                current_text, changes = self._remove_pii(current_text)
                result["operations_applied"].append("pii")
                result["metadata"]["changes_made"]["pii"] = changes
            elif op == "ocr":
                current_text, changes = self._fix_ocr_errors(current_text)
                result["operations_applied"].append("ocr")
                result["metadata"]["changes_made"]["ocr"] = changes
            elif op == "style":
                current_text, changes = self._convert_style(current_text, target_style)
                result["operations_applied"].append("style")
                result["metadata"]["changes_made"]["style"] = changes

        result["cleaned_text"] = current_text
        result["metadata"]["cleaned_length"] = len(current_text)

        return result

    def _fix_grammar(self, text: str) -> tuple:
        """Fix basic grammar issues using pattern matching."""
        changes = {"count": 0, "examples": []}
        original = text

        # Common patterns
        replacements = [
            (r"\bi\'m\b", "I'm", "Apostrophe correction"),
            (r"\byour\b(?=\s+going)", "you're", "your/you're confusion"),
            (r"\btheir\b(?=\s+(are|is))", "they're", "their/they're confusion"),
            (r"\bits\b(?=\s+(a|not|very))", "it's", "its/it's confusion"),
            (r"\bno\b(?=\s+one)", "no one", "Compound word"),
            (r"(?<!\w)u\b", "you", "Text speak"),
            (r"(?<!\w)ur\b", "your", "Text speak"),
            (r"(?<!\w)thru\b", "through", "Informal spelling"),
            (r"(?<!\w)b4\b", "before", "Text speak"),
        ]

        for pattern, replacement, desc in replacements:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                changes["examples"].append(desc)
                changes["count"] += matches

        return text, changes

    def _fix_extra_spaces(self, text: str) -> tuple:
        """Remove extra spaces and fix whitespace."""
        changes = {"count": 0, "removed_extra_spaces": 0}
        original_len = len(text)

        # Multiple spaces to single
        text = re.sub(r"  +", " ", text)

        # Spaces around punctuation
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        text = re.sub(r"([,.!?;:])\s+", r"\1 ", text)

        # Trim leading/trailing
        text = text.strip()

        # Fix space before line breaks
        text = re.sub(r" +\n", "\n", text)
        text = re.sub(r"\n +", "\n", text)

        changes["removed_extra_spaces"] = original_len - len(text)
        if changes["removed_extra_spaces"] > 0:
            changes["count"] = 1

        return text, changes

    def _standardize_capitalization(self, text: str) -> tuple:
        """Standardize capitalization: sentences start with capital, others lowercase."""
        changes = {"count": 0, "details": "Standardized capitalization"}
        original = text

        # Capitalize start of sentences
        text = re.sub(r"(?:^|\. |! |\? )([a-z])", lambda m: m.group(0)[:-1] + m.group(1).upper(), text)

        # Fix "i" to "I"
        text = re.sub(r"\bi\b", "I", text)

        # Lowercase start of sentences incorrectly capitalized mid-word
        sentences = re.split(r"(?<=[.!?])\s+", text)
        fixed_sentences = []
        for sent in sentences:
            if sent:
                # Capitalize first letter if it's a word
                sent = re.sub(r"^([a-z])", lambda m: m.group(1).upper(), sent)
                fixed_sentences.append(sent)

        text = " ".join(fixed_sentences)

        if text != original:
            changes["count"] = 1

        return text, changes

    def _remove_emojis(self, text: str) -> tuple:
        """Remove all emojis from text."""
        changes = {"count": 0, "removed_emojis": []}
        original = text

        # Find all emojis
        emoji_list = emoji.emoji_list(text)
        for item in emoji_list:
            changes["removed_emojis"].append(item["emoji"])

        # Remove emojis
        text = emoji.replace_emoji(text, replace="")

        changes["count"] = len(emoji_list)

        return text, changes

    def _clean_profanity(self, text: str) -> tuple:
        """Clean profanity by censoring with asterisks."""
        changes = {"count": 0, "censored": []}
        original = text

        # Find profanity
        words = text.split()
        censored_count = 0

        for i, word in enumerate(words):
            # Check if word contains profanity
            if profanity.contains_profanity(word):
                censored_word = profanity.censor(word)
                if censored_word != word:
                    changes["censored"].append(word)
                    censored_count += 1
                words[i] = censored_word

        text = " ".join(words)
        changes["count"] = censored_count

        return text, changes

    def _remove_pii(self, text: str) -> tuple:
        """Remove personally identifiable information using Presidio."""
        changes = {"count": 0, "entities_removed": []}

        try:
            # Analyze for PII
            results = self.analyzer.analyze(
                text=text,
                language="en",
            )

            # Anonymize found entities
            if results:
                anonymize_config = {
                    "DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
                }
                anonymized_text = self.anonymizer.anonymize(
                    text=text, analyzer_results=results, operators=anonymize_config
                )
                text = anonymized_text.text
                changes["count"] = len(results)
                changes["entities_removed"] = [
                    f"{r.entity_type}" for r in results
                ]
        except Exception:
            # If Presidio fails, do basic pattern matching
            patterns = [
                (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN REDACTED]"),  # SSN
                (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[CARD REDACTED]"),  # Credit card
                (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL REDACTED]"),  # Email
                (r"\b\d{10}\b", "[PHONE REDACTED]"),  # Phone
            ]

            for pattern, replacement in patterns:
                matches = len(re.findall(pattern, text))
                if matches > 0:
                    text = re.sub(pattern, replacement, text)
                    changes["entities_removed"].append(pattern)
                    changes["count"] += matches

        return text, changes

    def _fix_ocr_errors(self, text: str) -> tuple:
        """Fix common OCR mistakes."""
        changes = {"count": 0, "corrections": []}
        original = text

        # Common OCR errors (character confusion)
        ocr_corrections = [
            (r"\b0\b", "o", "Zero to O"),  # 0 -> O in words
            (r"\bl\b", "I", "l to I (uppercase)"),  # lowercase L to I
            (r"\b1\b", "l", "1 to l"),  # 1 to lowercase l
            (r"\brn\b", "m", "rn to m"),  # rn looks like m
            (r"\bvv\b", "w", "vv to w"),  # double v looks like w
            (r"\bcl\b", "d", "cl to d"),  # cl looks like d
            (r"\brn\b", "m", "rn to m"),  # rn to m
            (r"\bii\b", "u", "ii to u"),  # double i to u
            (r"＄", "$", "Full-width dollar"),  # Full-width chars
            (r"（", "(", "Full-width parenthesis"),
            (r"）", ")", "Full-width parenthesis"),
        ]

        for pattern, replacement, desc in ocr_corrections:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
                changes["corrections"].append(desc)
                changes["count"] += matches

        # Use ftfy to fix encoding issues
        try:
            text = ftfy.fix_text(text)
        except Exception:
            pass

        return text, changes

    def _convert_style(self, text: str, target_style: str = "formal") -> tuple:
        """Convert text to different writing styles."""
        changes = {"count": 1, "target_style": target_style, "description": ""}
        original = text

        if target_style == "formal":
            # Replace contractions with full forms
            contractions = [
                (r"\bcan't\b", "cannot"),
                (r"\bwon't\b", "will not"),
                (r"\bdon't\b", "do not"),
                (r"\bisn't\b", "is not"),
                (r"\baren't\b", "are not"),
                (r"\bwasn't\b", "was not"),
                (r"\bweren't\b", "were not"),
                (r"\bhadn't\b", "had not"),
                (r"\bhasn't\b", "has not"),
                (r"\bhaven't\b", "have not"),
                (r"\b'll\b", " will"),
                (r"\b've\b", " have"),
                (r"\b'd\b", " would"),
                (r"\b're\b", " are"),
            ]
            for contraction, formal in contractions:
                text = re.sub(contraction, formal, text, flags=re.IGNORECASE)

            # Remove slang
            text = re.sub(r"\bkinda\b", "kind of", text, flags=re.IGNORECASE)
            text = re.sub(r"\bgotta\b", "got to", text, flags=re.IGNORECASE)
            text = re.sub(r"\bwanna\b", "want to", text, flags=re.IGNORECASE)
            text = re.sub(r"\bthru\b", "through", text, flags=re.IGNORECASE)
            changes["description"] = "Converted to formal style"

        elif target_style == "casual":
            # Add conversational tone (minimal)
            text = re.sub(r"\bcannot\b", "can't", text, flags=re.IGNORECASE)
            text = re.sub(r"\bwill not\b", "won't", text, flags=re.IGNORECASE)
            changes["description"] = "Converted to casual style"

        elif target_style == "technical":
            # Standardize technical terminology
            replacements = [
                (r"\buse\b", "utilize", "General to technical"),
                (r"\bget\b", "obtain", "General to technical"),
                (r"\bmake\b", "generate", "General to technical"),
            ]
            for informal, technical, _ in replacements:
                text = re.sub(informal, technical, text, flags=re.IGNORECASE)
            changes["description"] = "Converted to technical style"

        elif target_style == "simple":
            # Replace complex words with simpler ones
            replacements = [
                (r"\butilize\b", "use"),
                (r"\bchallenging\b", "hard"),
                (r"\buccess\b", "try"),
                (r"\belucidate\b", "explain"),
                (r"\ncomprehensive\b", "complete"),
            ]
            for complex_word, simple_word in replacements:
                text = re.sub(complex_word, simple_word, text, flags=re.IGNORECASE)
            changes["description"] = "Converted to simple style"

        return text, changes


def get_text_cleaner() -> TextCleaner:
    """Factory function to get TextCleaner instance (for DI)."""
    return TextCleaner()
