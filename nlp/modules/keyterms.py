import csv
import numpy as np
import textacy
import textacy.preprocessing
import textacy.extract
import matplotlib.pyplot as plt

def decompose_keyterms(keyterm_list):
    '''Creates two lists from a list of tuples.

    Input:
        keyterm_list: a list of tuples containing keyterms and scores.
        
    Returns:
        terms: a list of keyterms as strings
        scores: a list of the correspinding scores'''
  
    terms = [el[0].replace(' ', '\n') for el in keyterm_list]
    scores = np.asarray([el[1] for el in keyterm_list])
    return terms, scores

def make_barplot(scores,keyterms,ax=None,
    title='barplot',
    ylabel='ylabel',
    color='lightblue',
    edgecolor='midnightblue',
    align='center',
    alpha=1.0):
  
    'Plots barplot onto an axes object'''
     
    bars = ax.bar(np.arange(len(keyterms)),
            scores,
            align=align,
            color=color,
            alpha=alpha)
    for bar in bars:
        bar.set_edgecolor(edgecolor)

    ax.set_xticks(np.arange(len(keyterms)))
    ax.set_xticklabels(keyterms,fontsize=5)
    ax.set_ylabel(ylabel,fontsize=12)
    ax.set_title(title,fontsize=12)
    return ax

def write_results(scores,keyterms,writer):
    
    '''Writes the keyterms and scores to row in csv'''
    
    keyterms = [term.replace('\n', ' ') for term in keyterms]
    writer.writerow(keyterms)
    writer.writerow(scores)

def create_keyterm_graph(name,text,file_png,file_csv):

    # Create doc object using SpaCy's en_core_web_sm model
    doc = textacy.make_spacy_doc(text, lang='en_core_web_sm')

    # Each algorithm returns a list of tuples, containing the keyterm and a score
    textrank = textacy.extract.keyterms.textrank(doc,normalize="lemma")
    yake = textacy.extract.keyterms.yake(doc,normalize="lemma")
    scake = textacy.extract.keyterms.scake(doc,normalize="lemma")
    sgrank = textacy.extract.keyterms.sgrank(doc,normalize="lemma")

    # Separate terms and scores into lists to help with plotting
    terms_textrank, scores_textrank  = decompose_keyterms(textrank)
    terms_yake, scores_yake  = decompose_keyterms(yake)
    terms_scake, scores_scake  = decompose_keyterms(scake)
    terms_sgrank, scores_sgrank  = decompose_keyterms(sgrank)

    # Make plot using the make_barplot function
    fig, axes = plt.subplots(2,2,figsize=(11,8))
    make_barplot(scores_textrank, terms_textrank,axes[0,0],title='TextRank algorithm',ylabel='Importance')
    make_barplot(scores_yake,terms_yake,axes[0,1],title='YAKE algorithm',ylabel='Importance',color='lightcoral',edgecolor='firebrick')
    make_barplot(scores_scake,terms_scake,axes[1,0],title='sCAKE algorithm', ylabel='Importance',color='springgreen',edgecolor='darkgreen')
    make_barplot(scores_sgrank,terms_sgrank,axes[1,1],title='SGRank algorithm', ylabel='Importance',color='moccasin',edgecolor='darkorange')
    plt.tight_layout()
    plt.savefig(file_png,dpi=300)

    # Save results to csv
    with open(file_csv, mode='w') as f:
        writer = csv.writer(f, delimiter=',')
        write_results(keyterms=terms_textrank, scores=scores_textrank, writer=writer)
        write_results(keyterms=terms_yake, scores=scores_yake, writer=writer)
        write_results(keyterms=terms_scake, scores=scores_scake, writer=writer)
        write_results(keyterms=terms_sgrank, scores=scores_sgrank, writer=writer)