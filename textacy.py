import textacy


text = (
    "Since the so-called \"statistical revolution\" in the late 1980s and mid 1990s, "
    "much Natural Language Processing research has relied heavily on machine learning. "
    "Formerly, many language-processing tasks typically involved the direct hand coding "
    "of rules, which is not in general robust to natural language variation. "
    "The machine-learning paradigm calls instead for using statistical inference "
    "to automatically learn such rules through the analysis of large corpora "
    "of typical real-world examples."
)

# understand keywords
list(textacy.extract.keyword_in_context(text, "language", window_width=25, pad_context=True))

# clean the data (normalize whitespace, remove punction etc.)
textacy.preprocessing.normalize.whitespace(textacy.preprocessing.remove.punctuation(text))[:80]

# make a doc
metadata = {
    "title": "Natural-language processing",
    "url": "https://en.wikipedia.org/wiki/Natural-language_processing",
    "source": "wikipedia",
}
doc = textacy.make_spacy_doc((text, metadata))

# extracting various elements of interest
list(textacy.extract.ngrams(doc, 3, filter_stops=True, filter_punct=True, filter_nums=False))
list(textacy.extract.ngrams(doc, 2, min_freq=2))
list(textacy.extract.entities(doc, drop_determiners=True))

# indentifying key terms
textacy.extract.textrank(doc, normalize="lemma", topn=10)
textacy.extract.sgrank(doc, ngrams=(1, 2, 3, 4), normalize="lower", topn=0.1)

# computing readability statistics
ts = textacy.TextStats(doc)
ts.n_words, ts.n_syllables, ts.n_chars
ts.entropy
ts.flesch_kincaid_grade_level, ts.flesch_reading_ease
ts.lix

# transform docuemnt to bag of terms
bot = doc._.to_bag_of_terms(ngrams=(1, 2, 3), entities=True, weighting="count", as_strings=True)
sorted(bot.items(), key=lambda x: x[1], reverse=True)[:15]

# loading a single text file
texts = textacy.io.read_text('~/Desktop/burton-tweets.txt', lines=True)
for text in texts:
    doc = textacy.make_spacy_doc(text)
    print(doc._.preview)

# loading a json file
records = textacy.io.read_json(
    "textacy/data/capitol_words/capitol-words-py3.json.gz",
    mode="rt", lines=True)
for record in records:
    doc = textacy.make_spacy_doc((record["text"], {"title": record["title"]}))
    print(doc._.preview)
    print("meta:", doc._.meta)
    # do stuff...
    break

# making a corpus
corpus = textacy.Corpus("en", data=records)

# something happening here...
textacy.Corpus(textacy.load_spacy_lang("en_core_web_sm", disable=("parser", "tagger")), data=ds.texts(speaker_party="R", chamber="House", limit=100))

# selecting documents in a corpus
corpus[-1]._.preview
[doc._.preview for doc in corpus[10:15]]
obama_docs = list(corpus.get(lambda doc: doc._.meta["speaker_name"] == "Barack Obama"))
len(obama_docs)

# get named entities
list(textacy.extract.ngrams(docx_0,3))