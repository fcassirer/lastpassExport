

# Lastpass to Bitwarden export corrector

## Problem

Lastpass exports a quoted multiline CSV that while properly formatted, is problematic for Bitwarden to import.   Many secure notes have multiple lines and these fail to import properly in bitwarden.

## Solution

Reformat the CSV so that it can be more easily imported into Bitwarden. Ideally, this code would just generate a bitwarden json formatted import file which can correctly handle embedded newlines in notes and many other things that have to be tweaked in the CSV to get it to even import.  Howevever, I didn't go that far.  To get this working more quickly I instead chose to also include a bitwarden json reader/writer.   The reader/writer can further tweak what was imported via the CSV.  Here is the basic sequence to get the best result:

* Export your data from LastPass
* Run this script against the LastPass CSV to produce a CSV that can be imported into Bitwarden
* Purge your Bitwarden vault to have a clean starting point (optional)
* import the output CSV into Bitwarden
* export your Bitwarden vault as a Bitwarden json file
* Run this script *again* using the above Bitwarden json file as input, output to a new json, i.e, `-o tweakedBitwarden.json`)
* Purge your Bitwarden vault to have a clean starting point (recommended to avoid duplicates)
* Marvel at how all of this was necessary to achieve something Bitwarden should be natively providing ;-)

### Process

- Read the lastpass export csv file using the python csv reader, this will properly read multiline fields as emitted by lastpass (but not properly handled by bitwarden).
- We then take the incoming records, place them into a list and embed \n into the notes fields.
- While we are loading up the csv data, hash the record and skip any duplicates as it seems that lastpass likes to double the data in the exported csv ;-(
- We then write out the new csv.

- The new csv will cleanly import into bitwarden ... but, you aren't done yet as bitwarden won't honor the embedded \n's (sheesh).
- The imported records will have a single line for all notes.  To complete the conversion, use the bitwarden export to export to a .json file, then run:

``
$ sed -e 's/\\\\n/\\n/g' bitwarden-export.json >bitwarden-export-with-newlines.json
``

This will replace the `\\n`'s with a non-escaped `\n` which bitwarden will then properly import when reading its own json export format.   The script will also map many of the LastPass 'secureNote' type records into a Bitwarden identity entry.  Any common fields are mapped (as best as I was able to), fields that have no native Bitwarden match are automatically converted to custom text fields.  To get the most recent field mapping list, look at the `lpmap_identity{}` and `lpmap_card{}` hashes in `lpe.py`

- Purge your bitwarden vault, reload the bitwarden page (it doesn't always refresh properly, another bitwarden bug), followed by an import of the bitwarden-export-with-newlines.json file.   This appears to re-instate the newlines properly and your text fields will be similar to how they were formatted in lastpass

## Notes

- Bitwarden doesn't handle embededed newlines in text fields, need to export as json, massage the newlines, and re-import to get it correct
- Bitwarden doesn't always refresh the vault after purging, be sure to reload the vault after each import

##  Way too much work for something that should just be included in the import/export process, but ... it worked.
