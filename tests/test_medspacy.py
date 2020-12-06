import pytest

import nlp_preprocessor
import medspacy
import spacy


class TestMedSpaCy:
    def test_default_load(self):
        nlp = medspacy.load()
        expected_pipe_names = {
            "tagger",
            "parser",
            "sentencizer",
            "context",
            "target_matcher",
            "sectionizer",
            "postprocessor",
        }
        assert set(nlp.pipe_names) == expected_pipe_names
        assert isinstance(nlp.tokenizer, nlp_preprocessor.Preprocessor)

    def test_load_enable(self):
        nlp = medspacy.load(enable=["target_matcher"])
        assert len(nlp.pipeline) == 1
        assert "target_matcher" in nlp.pipe_names
        assert isinstance(nlp.tokenizer, spacy.tokenizer.Tokenizer)

    def test_nlp(self):
        nlp = medspacy.load()
        assert nlp("This is a sentence. So is this.")

    def test_load_disable(self):
        nlp = medspacy.load(disable=["tagger", "parser"])
        expected_pipe_names = {
            "sentencizer",
            "target_matcher",
            "context",
            "sectionizer",
            "postprocessor",
        }
        assert set(nlp.pipe_names) == expected_pipe_names
        assert isinstance(nlp.tokenizer, nlp_preprocessor.Preprocessor)

    def test_load_rules(self):
        nlp = medspacy.load(load_rules=True)
        context = nlp.get_pipe("context")
        assert context.item_data
        sectionizer = nlp.get_pipe("sectionizer")
        assert sectionizer.patterns

    def test_load_quickumls(self):
        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = medspacy.load(enable=["quickumls"])
        quickumls = nlp.get_pipe("QuickUMLS matcher")
        assert quickumls
        # this is a member of the QuickUMLS algorithm inside the component
        assert quickumls.quickumls
        # Check that the simstring database exists
        assert quickumls.quickumls.ss_db

        # TODO -- Consider moving this and other extraction tests to separate tests from loading
        doc = nlp('Decreased dipalmitoyllecithin content found in lung specimens')

        assert len(doc.ents) == 1

        entity_spans = [ent.text for ent in doc.ents]

        assert 'dipalmitoyllecithin' in entity_spans

    def test_not_load_rules(self):
        nlp = medspacy.load(load_rules=False)
        context = nlp.get_pipe("context")
        assert not context.item_data
        sectionizer = nlp.get_pipe("sectionizer")
        assert not sectionizer.patterns
