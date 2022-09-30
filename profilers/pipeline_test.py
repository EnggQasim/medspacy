import cProfile
from functools import wraps
import sys

sys.path = [
    "/Users/u6022257/opt/anaconda3/lib/python39.zip",
    "/Users/u6022257/opt/anaconda3/lib/python3.9",
    "/Users/u6022257/opt/anaconda3/lib/python3.9/lib-dynload",
    "/Users/u6022257/opt/anaconda3/lib/python3.9/site-packages/aeosa",
    "/Users/u6022257/opt/anaconda3/lib/python3.9/site-packages/medspacy_quickumls-2.3-py3.9.egg",
    "/Users/u6022257/opt/anaconda3/lib/python3.9/site-packages/quickumls_simstring-1.1.5.post1-py3.9-macosx-10.9-x86_64.egg",
    "../",
    "../medspacy",
    "/Users/u6022257/opt/anaconda3/lib/python3.9/site-packages/",
]
print(sys.path)
import medspacy


# load spacy model
nlp = medspacy.load()  # YES

# tokenizing and sentence splitting
import spacy

with open("../notebooks/discharge_summary.txt") as f:
    text = f.read()
nlp = spacy.blank("en")
from medspacy.custom_tokenizer import create_medspacy_tokenizer

medspacy_tokenizer = create_medspacy_tokenizer(nlp)  # YES
default_tokenizer = nlp.tokenizer
example_text = r"Pt c\o n;v;d h\o chf+cp"
print("Tokens from default tokenizer:")
print(list(default_tokenizer(example_text)))
print("Tokens from medspacy tokenizer:")
print(list(medspacy_tokenizer(example_text)))  # YES
from medspacy.sentence_splitting import PyRuSHSentencizer

nlp.add_pipe("medspacy_pyrush")
print(nlp.pipe_names)
doc = nlp(example_text)

# taget matcher
nlp = medspacy.load(enable=["pyrush"])
from medspacy.ner import TargetMatcher, TargetRule

target_matcher = TargetMatcher(nlp)
target_matcher = nlp.add_pipe("medspacy_target_matcher")
target_rules1 = [
    TargetRule(literal="abdominal pain", category="PROBLEM"),
    TargetRule("stroke", "PROBLEM"),
    TargetRule("hemicolectomy", "TREATMENT"),
    TargetRule("Hydrochlorothiazide", "TREATMENT"),
    TargetRule("colon cancer", "PROBLEM"),
    TargetRule("metastasis", "PROBLEM"),
]
target_matcher.add(target_rules1)
doc = nlp(text)
print(nlp.pipe_names)
for ent in doc.ents:
    print(ent, ent.label_, ent._.target_rule.literal, sep="  |  ")
    print()
pattern_rules = [
    TargetRule(
        "radiotherapy", "PROBLEM", pattern=[{"LOWER": {"IN": ["xrt", "radiotherapy"]}}]
    ),
    TargetRule(
        "diabetes", "PROBLEM", pattern=r"type (i|ii|1|2|one|two) (dm|diabetes mellitus)"
    ),
]
target_matcher.add(pattern_rules)
from spacy.tokens import Span

Span.set_extension("icd10", default="")
target_rules2 = [
    TargetRule(
        "Type II Diabetes Mellitus",
        "PROBLEM",
        pattern=[
            {"LOWER": "type"},
            {"LOWER": {"IN": ["2", "ii", "two"]}},
            {"LOWER": {"IN": ["dm", "diabetes"]}},
            {"LOWER": "mellitus", "OP": "?"},
        ],
        attributes={"icd10": "E11.9"},
    ),
    TargetRule(
        "Hypertension",
        "PROBLEM",
        pattern=[{"LOWER": {"IN": ["htn", "hypertension"]}}],
        attributes={"icd10": "I10"},
    ),
]
target_matcher.add(target_rules2)

doc = nlp(text)
for ent in doc.ents:
    if ent._.icd10 != "":
        print(ent, ent._.icd10)
# context
from medspacy.context import ConTextComponent, ConTextRule

context = ConTextComponent(nlp, rules="default")
context = nlp.add_pipe("medspacy_context", config={"rules": "default"})
context_rules = [
    ConTextRule(
        "diagnosed in <YEAR>",
        "HISTORICAL",
        rule="BACKWARD",  # Look "backwards" in the text (to the left)
        pattern=[
            {"LOWER": "diagnosed"},
            {"LOWER": "in"},
            {"LOWER": {"REGEX": "^[\d]{4}$"}},
        ],
    )
]
context.add(context_rules)
# Detect Section
from medspacy.section_detection import Sectionizer

sectionizer = Sectionizer(nlp, rules="default")
sectionizer = nlp.add_pipe("medspacy_sectionizer")
from medspacy.section_detection import SectionRule

section_rules = [
    SectionRule(literal="Brief Hospital Course:", category="hospital_course"),
    SectionRule(
        "Major Surgical or Invasive Procedure:",
        "procedure",
        pattern=r"Major Surgical( or |/)Invasive Procedure:",
    ),
    SectionRule(
        "Assessment/Plan",
        "assessment_and_plan",
        pattern=[
            {"LOWER": "assessment"},
            {"LOWER": {"IN": ["and", "/", "&"]}},
            {"LOWER": "plan"},
        ],
    ),
]
sectionizer.add(section_rules)
# preprocessing
from medspacy.preprocess import Preprocessor, PreprocessingRule
import re

preprocessor = Preprocessor(nlp.tokenizer)
preprocess_rules = [
    lambda x: x.lower(),
    PreprocessingRule(
        re.compile("\[\*\*[\d]{1,4}-[\d]{1,2}(-[\d]{1,2})?\*\*\]"),
        repl="01-01-2010",
        desc="Replace MIMIC date brackets with a generic date.",
    ),
    PreprocessingRule(
        re.compile("\[\*\*[\d]{4}\*\*\]"),
        repl="2010",
        desc="Replace MIMIC year brackets with a generic year.",
    ),
    PreprocessingRule(
        re.compile("dx'd"), repl="Diagnosed", desc="Replace abbreviation"
    ),
    PreprocessingRule(re.compile("tx'd"), repl="Treated", desc="Replace abbreviation"),
    PreprocessingRule(
        re.compile("\[\*\*[^\]]+\]"),
        desc="Remove all other bracketed placeholder text from MIMIC",
    ),
]
preprocessor.add(preprocess_rules)
nlp.tokenizer = preprocessor

print(nlp.pipe_names)
preprocessed_doc = nlp(text)
print("Hello")