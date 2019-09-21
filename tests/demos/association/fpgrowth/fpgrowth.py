
import csv
import json
import pyfpgrowth
import pprint

loadpath = '/home/benjamin/Documents/HII-C/Knowledge/tests/demos/association/data.csv'
savepath = '/home/benjamin/Documents/HII-C/Knowledge/tests/demos/association/fpgrowth/results.json'

loadfile = open(loadpath, 'r')
parser = csv.reader(loadfile, delimiter=',', quotechar='"')
top = next(parser)
cols = {key: val for key, val in zip(top, range(len(top)))}

transactions = []
transaction = []
invoice = 0
prev_invoice = 0

for item in parser:
    invoice = str(item[cols['InvoiceNo']])
    if invoice != prev_invoice:
        if len(transaction):
            transactions.append(transaction)
        transaction = []
    transaction.append(str(item[cols['StockCode']]))
    prev_invoice = invoice

loadfile.close()

patterns = pyfpgrowth.find_frequent_patterns(transactions, 500)
associations = pyfpgrowth.generate_association_rules(patterns, 0.7)

pprint.pprint(associations)

# with open(savepath, 'w') as savefile:
#     json.dump(associations, savefile)