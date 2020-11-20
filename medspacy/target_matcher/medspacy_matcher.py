from spacy.matcher import Matcher, PhraseMatcher
from .regex_matcher import RegexMatcher

from spacy.tokens import Span

class MedspacyMatcher:
    def __init__(self, nlp):
        self.nlp = nlp
        self._rule_ids = set()
        self._rules = list()
        self.labels = set()
        self._rule_item_mapping = dict()

        self.matcher = Matcher(self.nlp.vocab)
        self.phrase_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self.regex_matcher = RegexMatcher(self.nlp.vocab)


    def add(self, rules):
        """Add a list of targetRules to the matcher."""
        i = len(self._rules)
        self._rules += rules

        for rule in rules:
            self.labels.add(rule.category)
            rule_id = f"{rule.category}_{i}"
            rule._rule_id = rule_id
            self._rule_item_mapping[rule_id] = rule
            if rule.pattern is not None:
                # If it's a string, add a RegEx
                if isinstance(rule.pattern, str):
                    self.regex_matcher.add(rule_id, [rule.pattern], rule.on_match)
                # If it's a list, add a pattern dictionary
                elif isinstance(rule.pattern, list):
                    self.matcher.add(rule_id, [rule.pattern], on_match=rule.on_match)
                else:
                    raise ValueError("The pattern argument must be either a string or a list, not {0}".format(type(rule.pattern)))
            else:
                self.phrase_matcher.add(rule_id, [self.nlp.make_doc(rule.literal.lower())], on_match=rule.on_match)
            i += 1

    def __call__(self, doc):
        matches = self.matcher(doc)
        matches += self.phrase_matcher(doc)
        matches += self.regex_matcher(doc)
        matches = prune_overlapping_matches(matches)
        return matches

def prune_overlapping_matches(matches, strategy="longest"):
    if strategy != "longest":
        raise NotImplementedError()

    # Make a copy and sort
    unpruned = sorted(matches, key=lambda x: (x[1], x[2]))
    pruned = []
    num_matches = len(matches)
    if num_matches == 0:
        return matches
    curr_match = unpruned.pop(0)

    while True:
        if len(unpruned) == 0:
            pruned.append(curr_match)
            break
        next_match = unpruned.pop(0)

        # Check if they overlap
        if overlaps(curr_match, next_match):
            # Choose the larger span
            longer_span = max(curr_match, next_match, key=lambda x: (x[2] - x[1]))
            pruned.append(longer_span)
            if len(unpruned) == 0:
                break
            curr_match = unpruned.pop(0)
        else:
            pruned.append(curr_match)
            curr_match = next_match
    # Recursive base point
    if len(pruned) == num_matches:
        return pruned
    # Recursive function call
    else:
        return prune_overlapping_matches(pruned)

def overlaps(a, b):
    if _span_overlaps(a, b) or _span_overlaps(b, a):
        return True
    return False

def _span_overlaps(a, b):
    _, a_start, a_end = a
    _, b_start, b_end = b
    if a_start >= b_start and a_start < b_end:
        return True
    if a_end > b_start and a_end <= b_end:
        return True
    return False

def matches_to_spans(doc, matches, set_label=True):
    spans = []
    for (rule_id, start, end) in matches:
        if set_label:
            label = doc.vocab.strings[rule_id]
        else:
            label = None
        spans.append(Span(doc, start=start, end=end, label=label))
    return spans

