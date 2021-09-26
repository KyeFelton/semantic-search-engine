''' This workflow explores the some basic use cases for textacy across the corpus '''

import textacy
import textacy.preprocessing
import collections
import itertools
import textacy.extract
from functools import partial
import textacy.representations
import textacy.tm

# Load the data
data = textacy.io.read_json('./data/cleaned/page.json', mode='rt', lines=False)

# Prepare the preprocessign pipeline
preproc = textacy.preprocessing.make_pipeline(
    textacy.preprocessing.normalize.bullet_points,
    textacy.preprocessing.normalize.unicode,
    textacy.preprocessing.normalize.quotation_marks,
    textacy.preprocessing.normalize.whitespace,
)

# Create the corpus
docs = []
for record in data:
    for page in record:
        for content in page['content']:
            text = preproc(content)
            meta = {'url': page['url'], 'title': page['title'], 'category': page['category']}
            docs.append((text, meta))
corpus = textacy.Corpus('en_core_web_sm', data=docs)
print(corpus)

# Inspect the counts of each category
# print(corpus.agg_metadata('category', collections.Counter))

# Inspect the most common descriptions of students
patterns = [{'POS': {'IN': ['ADJ', 'DET']}, 'OP': '+'}, {'ORTH': {'REGEX': 'students?'}}]
matches = itertools.chain.from_iterable(textacy.extract.token_matches(doc, patterns) for doc in corpus)
# print(collections.Counter(match.lemma_ for match in matches).most_common(20))

# Inspect the most common keywords said in docs mentioning students
kt_weights = collections.Counter()
for doc in corpus.get(lambda doc: any(doc._.extract_regex_matches('students?'))):
    keyterms = doc._.extract_keyterms(
        'textrank', normalize='lemma', window_size=10, edge_weighting='count', topn=10
    )
    kt_weights.update(dict(keyterms))
# print(kt_weights.most_common(20))

# Extract entities
terms = (
    textacy.extract.terms(
        doc,
        ngs=partial(textacy.extract.ngrams, n=2, include_pos={'NOUN', 'ADJ'}),
        ents=partial(textacy.extract.entities, include_types={'PERSON', 'ORG', 'GPE', 'LOC'}))
    for doc in corpus)

# Lemmatize entities
tokenized_docs = (
    textacy.extract.terms_to_strings(term, by='lemma')
    for term in terms)

# Identify key topics across the corpus (using TF-IDF)
doc_term_matrix, vocab = textacy.representations.build_doc_term_matrix(tokenized_docs, tf_type='linear', idf_type='smooth')
model = textacy.tm.TopicModel('nmf', n_topics=10)
model.fit(doc_term_matrix)
doc_topic_matrix = model.transform(doc_term_matrix)
id_to_term = {id_: term for term, id_ in vocab.items()}
for topic_idx, terms in model.top_topic_terms(id_to_term, top_n=8):
    print(f"topic {topic_idx}: {' '.join(terms)}")
