import os
import os.path
import sys
import argparse
import re
import datetime
import hashlib

#import openpyxl
#from openpyxl import load_workbook,Workbook
#from openpyxl.utils import get_column_letter

import csv

parser = argparse.ArgumentParser(description="Lastpass Export Corrector")
parser.add_argument('-s','--securenotes',action='store_true', help="Strip secure notes")
parser.add_argument('-o','--output',type=str, default="out.csv", help="output csv name")
parser.add_argument('csvfile', type=str, nargs="?", default=None, help="Lastpass raw exported csv")

def debug(msg):
  #return
  print(msg)

def lastpassExport(dir = "." ):
  return

cargs = parser.parse_args()

#print(cargs.csvfile)


rows=[]
shamap={}
with open(cargs.csvfile, newline='') as csvf:
  reader=csv.reader(csvf, delimiter=',', quotechar='"')
  for row in reader:
    sha=hashlib.sha256((',').join(row).encode('utf-8')).hexdigest()
    if not sha in shamap:
      row[4] = row[4].replace("\n","\\n")
      shamap
      rows.append(row)
      shamap[sha] = 1

with open(cargs.output, 'w', encoding='utf-8') as o:
  writer = csv.writer(o,delimiter=',', quoting=csv.QUOTE_ALL)
  for row in rows:
    writer.writerow(row)
