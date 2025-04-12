# Connect to green then go to your scratch directory and download the files
# This download took me around 13 min
cd /scratch/bm3772
wget -r -np -nH --cut-dirs=1 -P pubmed_baseline ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/

# probably don't need the checksum files (md5) we can remove those

# 1.3k files each containing ~15k abstracts
# to unzip all of the files
gunzip pubmed_baseline/*.gz

# Test file
gunzip pubmed_baseline/baseline/pubmed25n0001.xml.gz  


