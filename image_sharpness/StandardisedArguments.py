# pylint: disable=C0103
"""
Functions which help standardise how commandline arguments are structured

"""
import argparse

def create_basic_parser(description):
    """
    Creates a basic argument parser with in and out arguments

    description:- the description to pass to the argument parser
    Return value:- an argparse parser object
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--out', nargs=1, required=True, help="The directory to output results to.")
    parser.add_argument('--input', nargs='+', required=True, help="A path to process.")
    return parser

def add_sharpness_arguments(parser):
    """
    Adds extra arguments to a parser for when determining image sharpness

    parser:- an argparse parser object to add the arguments to
    Return value:- the parser object that was passed in
    """
    parser.add_argument('--sharpness', action='store_true', help="If this argument is present, we determine image sharpness")
    
    return parser
