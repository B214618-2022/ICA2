#!/bin/python3
# myscript.py written on 16/11/2022 by B214618. Currently this is simply a base script to build the main script on.

import configparser
import argparse
import sys
import subprocess
#import requests
import re
import pandas as pd

# Initializing a parser object, to facilitate command line arguments to be passed to the program
args_parser = argparse.ArgumentParser(
    prog = "B214618's Protein conservation tool",
    description = "This program <content to be added>",
    epilog = "<content to be added>")

# Adding arguments...
args_parser.add_argument('--protein', dest='protein', default="pyruvate dehydrogenase", help = "protein query (e.g. \"Pyruvate dehydrogenase\")")
args_parser.add_argument('--group', dest='grouping', default="Ascomycota", help = "group query (e.g. \"Ascomycota\")")
args_parser.add_argument('--database', dest='database', default="protein", help = "NCBI database to query (e.g. \"protein\")")

# assigning parsed args to variable
args = args_parser.parse_args()
#print(args.protein, args.grouping)

# Creating empty dataframe to hold sequence info
seq_data = pd.DataFrame(columns = ['Accession', 'Protein name', 'Genus', 'Species', 'Sequence'])

# Fetching sequences the easy (boring) way
fasta_seqs = subprocess.check_output(f"esearch -db \"{args.database}\" -query \"{args.protein}[Protein Name] NOT partial[Properties]\" | efilter -organism \"{args.grouping}\" | efetch -format fasta", shell = True).decode('utf-8')
fasta_seqs_list = fasta_seqs.split('>')
# Filtering pesky empty list strings
fasta_seqs_list = list(filter(None, fasta_seqs_list))

list_of_rows=[]
# Slightly roundabout way of getting values to populate my dataframe...
for entry in fasta_seqs_list:
    accession_code = entry.split()[0]
    protein_name = re.search(r'(?<=' + accession_code + r')(.*)(?=\[)', entry).group(1).strip()
    species_block = re.search(r'(?<=\[)(.*)(?=\])', entry).group(1).split()
    genus = species_block[0]
    species = species_block[1]
    sequence = ''.join(entry.split('\n')[1:])
# Creating a list of lists that are rows of my final dataframe
    list_of_rows.append([accession_code, protein_name, genus, species, sequence])

# Creating the dataframe, with relevant column names...
seq_data = pd.DataFrame(list_of_rows, columns = ['Accession', 'Protein name', 'Genus', 'Species', 'Sequence'])

# I would really rather use variables for the whole process instead of writing to a .fa file, but I don't know how. Maybe this really is the best way to go about it!
file_for_msa = open("seqs.fa", "w")
file_for_msa.write(fasta_seqs)
file_for_msa.close()

# modified from python docs examples. Might be a more robust way of doing it?
subprocess.run("clustalo --auto --outfmt=msf -i seqs.fa -o align.msf", shell=True)
subprocess.run("plotcon align.msf -winsize 10 -graph png", shell=True)

# Takes an argument of an optional infile/outfile. if none is provided, it takes the standard input. 'nargs='?'' specifies that these are optional.
#parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
#parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)

# It felt like cheating to just be passing commands to the shell, so I decided to work out how to send and receive requests directly in python instead!
#print(f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db={database}&term={grouping}[Organism]+{protein}[Protein+Name]&usehistory=y")
#with requests.get(f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db={database}&term={grouping}[Organism]+AND{protein}[Protein+Name]&usehistory=y") as f:
#    xml_file = f.content.decode('utf-8')
#    webenv_match = re.search('(?<=<WebEnv>)(.*)(?=<\/WebEnv>)', xml_file)
#    querykey_match = re.search('(?<=<QueryKey>)(.*)(?=<\/QueryKey>)', xml_file)
#    if webenv_match:
#        web_env = webenv_match.group(1)
#        print('WebEnv key:' + web_env)
#    if querykey_match:
#        query_key = querykey_match.group(1)
#        print('Query key:' + query_key)

#print(f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db={database}&query_key={query_key}&WebEnv={web_env}&rettype=uilist&retmode=text")
#with requests.get(f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db={database}&query_key={query_key}&WebEnv={web_env}&rettype=uilist&retmode=text") as f:
#    my_file = f.content.decode('utf-8')
#    print(my_file)
