import tkinter
from PIL import Image as pilImage
from PIL import ImageTk as tkImage
import csv

import image_sharpness
import python_batch_processing




label = None
photoImage = None
filesIterator = None
files = None
nefImage = None
lastIndex = 1
currentRecord = []
results = [["filename", "wv", "pv", "wg", "pg", "s"]]


def main(args):
    global files, filesIterator, photoImage, label, lastIndex
    print("Finding NEF files...")
    files = getAllNefFiles(args.input)
    filesIterator = iter(files)

    
        
    top = tkinter.Tk()
    
    top.bind('x', imageSharp)
    top.bind('z', imageUnsharp)

    label = tkinter.Label()
    label.pack()

    nextImage()

    top.mainloop()
    return


def imageSharp(event):
    global currentRecord, results
    currentRecord.append(1)
    results.append(currentRecord)
    writeCsv()
    nextImage()

def writeCsv():
    global results
    with open('traindata.csv', 'w+') as csvfile:
        w = csv.writer(csvfile)
        w.writerows(results)

def imageUnsharp(event):
    global currentRecord, results
    currentRecord.append(0)
    results.append(currentRecord)
    writeCsv()
    nextImage()



def nextImage():
    global files, filesIterator, photoImage, label, lastIndex, currentRecord
    nefImagePath = next(filesIterator)
    isImage = image_sharpness.Image.fromFile(nefImagePath)
    wiVarSharpness = isImage.getWholeImageVarianceSharpness()
    afVarSharpness = isImage.getVarianceSharpnessForPrimaryAfPoint(lastIndex)
    wiGradSharpness = isImage.getWholeImageGradientSharpness()
    afGradSharpness = isImage.getGradientSharpnessForPrimaryAfPoint(lastIndex)
    currentRecord = [nefImagePath, wiVarSharpness, afVarSharpness, wiGradSharpness, afGradSharpness]
    tileImage = pilImage.fromarray(isImage.getPrimaryAfPointTile('rgb', lastIndex))
    lastIndex = isImage.getPrimaryAfPointIndex(lastIndex)
    photoImage = tkImage.PhotoImage(tileImage)
    label.config(image = photoImage)



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