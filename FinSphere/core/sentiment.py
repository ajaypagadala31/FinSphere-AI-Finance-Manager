"""Feedback sentiment using VADER (falls back to a tiny lexicon if vaderSentiment isn't installed)."""
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
except ImportError:
    _vader = None
_POS = {"good", "great", "love", "amazing", "awesome", "useful", "easy", "nice", "excellent", "best", "helpful"}
_NEG = {"bad", "poor", "hate", "slow", "terrible", "worst", "confusing", "useless", "broken", "bug"}


def analyze(text):
    if _vader:
        score = _vader.polarity_scores(text)["compound"]
    else:
        w = [x.strip(".,!?").lower() for x in text.split()]
        score = max(-1, min(1, (sum(x in _POS for x in w) - sum(x in _NEG for x in w)) / 3))
    label = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
    return label, round(score, 3)
