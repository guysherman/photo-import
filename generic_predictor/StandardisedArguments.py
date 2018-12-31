# pylint: disable=C0103
"""
Functions which help standardise how commandline arguments are structured

"""
import argparse


def add_arguments(parser):
    """
    Adds extra arguments to a parser for when determining image sharpness

    parser:- an argparse parser object to add the arguments to
    Return value:- the parser object that was passed in
    """
    parser.add_argument('--model', nargs=1, required=False, help="The json file which describes your model")
    
    return parser
