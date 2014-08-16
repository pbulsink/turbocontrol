#!/usr/bin/env python

import openbabel
import argparse

def convert_filetype(infile, outfile, intype='xyz', outtype='mol'):
    """Converts infile from intype (default xyz) to outtype (default mol)"""
    try:
        conv = openbabel.OBConversion()
        conv.OpenInAndOutFiles(infile, outfile)
        conv.SetInAndOutFormats(intype, outtype)
        conv.Convert()
        conv.CloseOutFile()
    except Exception as e:
        print "Error {}.".format(e)

def main():
    parser = argparse.ArgumentParser("Usage: %prog [options]")
    parser.add_argument('infile',
                        help="Read input from input FILE")
    parser.add_argument('outfile',
                        help='Write output to output FILE')
    parser.add_argument('-i', '--informat',
                        help="Read input format from file. Default .xyz")
    parser.add_argument('-o', '--outformat',
                        help="Write output format to file. Default .mol")
    args = parser.parse_args()
    if args.informat:
        if args.outformat:
            convert_filetype(args.infile, args.outfile, intype=args.informat,
                             outtype=args.outformat)
        else:
            convert_filetype(args.infile, args.outfile, intype=args.informat)
    elif args.outformat:
        convert_filetype(args.infile, args.outfile, outtype=args.outformat)
    else:
        convert_filetype(args.infile, args.outfile)
    exit()


if __name__ == '__main__':
    main()
