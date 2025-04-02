from Bio import Entrez
from Bio.Entrez import efetch
import json

 
with open('test_ground_truth.json') as f:
    ground_truth = json.load(f)
    Entrez.email = 'some@example.com'
    output_file = open("ground_truth_uilist.txt", 'a') 
    #removed for loop cycling through ground_truth.keys()
    #ret options: 
    # 1. retmode text and rettype abstract, medline, uilist
    # 2. retmode xml and rettype null (need to change output write for this)
    handle = efetch(db='pubmed', id=ground_truth.keys(), retmode='text', rettype='uilist')
    output_file.write(handle.read())
    output_file.close()
f.close()
            
