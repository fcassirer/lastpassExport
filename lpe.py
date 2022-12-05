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
import json

class ComplexEncoder(json.JSONEncoder):
     def default(self, obj):
         if isinstance(obj, complex):
             return [obj.real, obj.imag]
         # Let the base class default method raise the TypeError
         return json.JSONEncoder.default(self, obj)


parser = argparse.ArgumentParser(description="Lastpass Export Corrector")
parser.add_argument('-s','--securenotes',action='store_true', help="Strip secure notes")
parser.add_argument('-o','--output',type=str, default=None, help="output csv or json")
parser.add_argument('infile', type=str, nargs="?", default=None, help="Lastpass raw exported csv or json")
parser.add_argument('-v','--verbose', action='store_true', help="Debugging and other verbosities")

lpmap_identity={
  "Title" : "title",
  "First Name" : "firstName",
  "Middle Name" : "middleName",
  "Last Name" : "lastName",
  "Address" : "address1",
  "Address 1" : "address1",
  "Address 2" : "address2",
  "Adreess 3" : "address3",
  "City / Town" : "city",
  "State" : "state",
  "Zip / Postal Code" : "postalCode",
  "ZIP / Postal Code" : "postalCode",
  "Zip" : "postalCode",
  "ZIP" : "postalCode",
  "Postal Code" : "postalCode",
  "Country" : "country",
  "Company" : "company",
  "Email Address" : "email",
  "Phone" : "phone",
  "Social Security Number" : "ssn",
  "Username" : "username",
  "PassPort" : "passportNumber",
  "Driver's License Number" : "licenseNumber"
  }

lpmap_card = {
  "Name on Card" :"cardholderName",
  "Type" : "brand",
  "Number" : "number",
  "Expiration Month" : "expMonth",
  "Expiration Year" : "expYear",
  "Security Code" : "code"
}

monthtonumber = [
                  'January',
                  'February',
                  'March',
                  'April',
                  'May',
                  'June',
                  'July',
                  'August',
                  'September',
                  'October',
                  'November',
                  'December'
                  ]

cargs = parser.parse_args()

def debug(msg):
  #return
  if cargs.verbose:
    print("DEBUG: "+str(msg))

def lastpassExport(dir = "." ):
  return


def munge_csv():

  rows=[]
  shamap={}
  with open(cargs.infile, newline='') as csvf:
    reader=csv.reader(csvf, delimiter=',', quotechar='"')
    for row in reader:
      sha=hashlib.sha256((',').join(row).encode('utf-8')).hexdigest()
      if not sha in shamap:
        row[4] = row[4].replace("\n","\\n")
        shamap
        rows.append(row)
        shamap[sha] = 1

  closehandle = False
  if cargs.output:
    o = open(cargs.output, 'w', encoding='utf-8')
    closehandle = True
  else:
    o = sys.stdout

  writer = csv.writer(o,delimiter=',', quoting=csv.QUOTE_ALL)
  for row in rows:
    writer.writerow(row)

  if closehandle:
    o.close()

def bw_identity(ty, lpentry):
  ident = {}
  foundkeys = []
  for i in lpmap_identity.values():
    ident[i] = None
  for k in lpentry:
    if k in lpmap_identity.keys():
      ident[lpmap_identity[k]] = lpentry[k] if lpentry[k] != "" else None
      foundkeys.append(k)
    else:
      altk = (ty + " " + k)
      if  altk in lpmap_identity.keys():
        ident[lpmap_identity[altk]] = lpentry[k] if lpentry[k] != "" else None
        foundkeys.append(k)
#      else:
#        debug("ID: Unmapped Key: "+k)

  for k in foundkeys:
    del lpentry[k]
  return ident

def bw_card(ty, lpentry):
  card = {}
  for i in lpmap_card.values():
    card[i] = None
  for k in lpentry:
    if k in lpmap_card.keys():
      card[lpmap_card[k]] = lpentry[k] if lpentry[k] != "" else None

  return card

def bw_custom(ty, lpentry):
  cus = []
  for k in lpentry.keys():
    if k not in ["Notes"]:
      e = {
          "name": k,
          "value": lpentry[k] if lpentry[k] != "" else None,
          "type": 0,
          "linkedId": None
        }
      cus.append(e)

  return cus

def munge_json():
  try:
    with open(cargs.infile) as jf:
      vault = json.load(jf)
      row=-1
      for item in vault['items']:
        row += 1
        debug(str(row)+" INDEX: "+item['name'])
        if item['name'] == "Florida Drivers License": #"Ryan DCU checking":
          debug(item['name'])
        if 'notes' in item and item['notes'] is not None:
          if item['notes'].startswith("NoteType:"):
            lpitem = item['notes'][9:].split("\n")
            lpentry = {}
            debug(str(row)+" "+item['name']+" "+str(lpitem))
            for idx, e in enumerate(lpitem[1:]):
              k = e.split(':',1)
              if k[0] == "Notes":
                lpentry["Notes"] = "\n".join(lpitem[(idx+1):]).split(':',1)[1]
                break
              else:
                lpentry[k[0]] = k[1]
            nt = lpitem[0]
            if 'Notes' in lpentry:
              item['notes'] = lpentry['Notes'] if lpentry['Notes'] != "" else None

            # Do some normalization to map/split various LP fields to BW fields

            if 'Expiration Date' in lpentry:
              try:
                mdy = lpentry['Expiration Date'].split(',')
                mdy[0] = monthtonumber.index(mdy[0])+1
                if len(mdy) == 2:
                  if int(mdy[1]) > 31:
                    mdy.append(mdy[1])
                    mdy[1] = 1
              except ValueError:
                mdy = ["", 0, 0]

              lpentry['Expiration Year'] = str(mdy[2])
              lpentry['Expiration Month'] = str(mdy[0])

            if 'Name' in lpentry:
              try:
                nfields = (lpentry['Name'].split() + [None, None, None])[0:3]
              except ValueError:
                nfields = [None, None, None]

              lpentry['First Name'] = nfields[0]
              lpentry['Last Name'] = nfields[-1]
              if len(nfields) > 2:
                lpentry['Middle Name'] = nfields[1]
              del lpentry['Name']
              if 'Language' in lpentry:
                del lpentry['Language']

            if nt.startswith("Custom"):
              nt = "Custom"

            match nt:
              case "Social Security" |\
                   "Driver's License" |\
                   "Address" |\
                   "Membership" |\
                   "Bank Account" |\
                   "Custom" |\
                   "Passport":

                bw_item = bw_identity(nt,lpentry)
                del item['secureNote']
                item['type'] = 4
                item['identity'] = bw_item

                fields = bw_custom(nt, lpentry)
                if 'fields' not in item:
                  item['fields'] = []
                item['fields'] = item['fields'] + fields

              case "Credit Card":
                bw_item = bw_card(nt,lpentry)
                del item['secureNote']
                item['type'] = 3
                item['card'] = bw_item

              case "Server":
                # Leave as secure note
                continue

              case _:
                debug("Unknown: %s:" % (nt))


      closehandle = False
      if cargs.output:
        o = open(cargs.output, 'w', encoding='utf-8')
        closehandle = True
      else:
        o = sys.stdout

      # Write out json file
      try:
        o.write(json.dumps(vault, indent=4, sort_keys=True))
      except Exception as e:
        print("Could not write json output, err="+e.msg())

      if closehandle:
        o.close()

  except FileNotFoundError:
    print("Couldn't open json file")
    exit(1)

if (cargs.infile[-5:].casefold() == ".json".casefold()):
  munge_json()
else:
  munge_csv()
