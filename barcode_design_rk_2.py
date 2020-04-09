#!/usr/bin/env python


# Design DNA barcodes for sequencing experiments

import random
import csv

# This is from pypi python-levenshtein:
try:
    from Levenshtein import distance
except:
    print("python-levenshtein package not found, please install")


class BarcodeDesigner:

    def __init__(self,
                 number_of_barcodes=384,
                 barcode_length=11,
                 min_edit_distance=3,
                 input_barcodes=None):
        self.number_of_barcodes = number_of_barcodes
        self.barcode_length = barcode_length
        self.min_edit_distance = min_edit_distance
        self.input_barcodes = input_barcodes
        self.bases = ["A", "C", "G", "T"]

    def random_sequence(self):
        """Generate a random DNA sequence
        """
        return "".join([random.choice(self.bases)
                        for idx in range(self.barcode_length)])

    def random_sequences_iter(self):
        while True:
            yield self.random_sequence()

    def _edit_distance(self, seq1, seq2):
        return distance(seq1, seq2)


    def _is_good_barcode(self, seq, barcode_set):
        for barcode in barcode_set:
            if self._edit_distance(seq, barcode) < self.min_edit_distance:
                return False
        return True


    def generate_barcodes(self):
      barcode_set=set()
      newbarcode_set=set()
      with open(self.input_barcodes) as csv_file:
        barcode_reader = csv.reader(csv_file, delimiter=',')
        barcode_set = set([i[0] for i in list(barcode_reader)])
        for sequence in self.random_sequences_iter():
            if self._is_good_barcode(sequence, barcode_set):
              barcode_set.add(sequence)
              newbarcode_set.add(sequence)
              print("Generated %d barcodes" % len(barcode_set))
            if len(newbarcode_set) >= self.number_of_barcodes:
           		return newbarcode_set
      return newbarcode_set

    def barcode_set_stats(self, barcode_set, stats_file_name):
        stats = ""
        cycle_index = 1
        stats += "cycle nA nC nG nT\n"
        for cycle_content in zip(*map(list, barcode_set)):
            nA = sum([1
                      for base
                      in cycle_content
                      if base == "A"]) / float(len(barcode_set))
            nC = sum([1
                      for base
                      in cycle_content
                      if base == "C"]) / float(len(barcode_set))
            nG = sum([1
                      for base
                      in cycle_content
                      if base == "G"]) / float(len(barcode_set))
            nT = sum([1
                      for base
                      in cycle_content
                      if base == "T"]) / float(len(barcode_set))

            stats += "%d %.2f %.2f %.2f %.2f\n" % (cycle_index, nA, nC, nG, nT)
            cycle_index += 1

        stats += "\n------\n"
        stats += "barcode min_edit_distance\n"
        for barcode in sorted(barcode_set):
            min_edit_distance = min([self._edit_distance(barcode, obc)
                                     for obc in barcode_set
                                     if obc != barcode])
            stats += barcode + " " + str(min_edit_distance) + "\n"

        with open(stats_file_name, "w") as fp:
            fp.write(stats)

    def write_barcodes(self, barcode_set, fname):
        with open(fname, "w") as fp:
            for barcode in barcode_set:
                #print >> fp, barcode
                print(barcode, file=fp)



def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-o", "--output", dest="output", help="output prefix")
    parser.add_argument("-NB", "--NewBarcodes", dest="NewBarcodes", help="new barcode output prefix")
    parser.add_argument("-n",
                        "--number_of_barcodes",
                        dest="n_barcodes",
                        type=int,
                        default=384)
    parser.add_argument("-l",
                        "--length",
                        dest="length",
                        type=int,
                        default=11)
    parser.add_argument("-e",
                        "--min_edit_distance",
                        dest="min_edit_distance",
                        type=int,
                        default=3)
    parser.add_argument("-i", 
 		"--input_barcode_list", 
 		dest="input_barcode", 
 		type=str, default=None)
    args = parser.parse_args()

    bd = BarcodeDesigner(number_of_barcodes=args.n_barcodes,
                         barcode_length=args.length,
                         min_edit_distance=args.min_edit_distance,
                         input_barcodes=args.input_barcode)

    newbarcode_set = bd.generate_barcodes()
   # barcode_set,newbarcode_set 
    bd.barcode_set_stats(newbarcode_set, "%s.stats" % args.NewBarcodes)
    bd.write_barcodes(newbarcode_set, "%s.txt" % args.NewBarcodes)

    print("wrote %s.txt" % args.NewBarcodes)
    print("wrote %s.stats" % args.NewBarcodes)


if __name__ == "__main__":
    main()
