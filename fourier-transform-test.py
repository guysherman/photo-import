import tkinter
from PIL import Image as pilImage
from PIL import ImageTk as tkImage
import csv
import numpy as np

import image_sharpness
import python_batch_processing





labelFft = None
labelClr = None
photoImageFft = None
photoImageClr = None
filesIterator = None
files = None
nefImage = None
lastIndex = 1
currentRecord = []
results = [["filename", "a0", "a1", "a2", "a3"]]


def main(args):
    global files, filesIterator, photoImageFft, photoImageClr, labelFft, labelClr, lastIndex
    print("Finding NEF files...")
    files = getAllNefFiles(args.input)
    filesIterator = iter(files)

    while True:
        try:
            nextImage()
            print(".")
            
        except StopIteration:
            break
    
    writeCsv()

    return

def writeCsv():
    global results
    with open('traindata.csv', 'w+') as csvfile:
        w = csv.writer(csvfile)
        w.writerows(results)




def nextImage():
    global files, filesIterator, lastIndex, currentRecord
    nefImagePath = next(filesIterator)
    isImage = image_sharpness.Image(nefImagePath)
    
    tileArray = isImage.getPrimaryAfPointTile('l', lastIndex)
    fftArray = np.fft.fft2(tileArray, [512,512])
    
    r2 = fftArray.real ** 2
    i2 = fftArray.imag ** 2
    a = np.sqrt(np.add(r2, i2))[0:256, 0:256]
    a0 = a[0:128, 0:128]
    a1 = a[128:256, 0:128]
    a2 = a[0:128, 128:256]
    a3 = a[128:256, 128:256]

    avg0 = np.average(a0)
    avg1 = np.average(a1)
    avg2 = np.average(a2)
    avg3 = np.average(a3)

    currentRecord = [nefImagePath, avg0, avg1, avg2, avg3]
    results.append(currentRecord)


def getAllNefFiles(inputLocations):
    """
    Uses the recursive search functionality to return a list of NEF files

    inputLocations:- a list of locations to search below
    returns:- a list of all the NEF files found below each of the search locations
    """
    searcher = python_batch_processing.RecursiveSearch.RecursiveSearch(
        lambda path: path.lower().endswith(".nef"))
    files = searcher.search_many(inputLocations)
    return sorted(files)


if __name__ == "__main__":
    parser = python_batch_processing.StandardisedArguments.create_basic_parser(
        "Import digital photos from a memory card into a nice structure")
    parser = image_sharpness.StandardisedArguments.add_sharpness_arguments(parser)
    arguments = parser.parse_args()
    main(arguments)