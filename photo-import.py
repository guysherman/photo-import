"""
Imports photos (typically from a memory card, but generally 1 or more locations on the file system)
and organises them into a structure, EXIF Year/EXIF Month/EXIF Day/Camera/Volume, where each
"Volume" has at most 250 photos in it. The volumes thing is to play nice with Google Drive's file
browser implementation on iOS.
"""
# pylint: disable=C0103
import os
import shutil
import re

import exifread
import numpy as np


import python_batch_processing
import image_sharpness

CAMERA_TAG = "Image Model"
DATE_TAG = "Image DateTime"

lastIndex = 1

#RELEVANT_TAGS = ['Image DateTime', 'Image Model'],


DATETIME_RE = re.compile(r"(\d\d\d\d):(\d\d):(\d\d) \d\d:\d\d:\d\d")

def main(args):
    """
        The main function of the program. Orchestrates the work
    """
    print("Finding NEF files...")
    files = getAllNefFiles(args.input)
    
    if args.sharpness == True:
        print("Sorting sharp from unsharp...")
        sharp, questionable, unsharp = sortSharpFromUnsharp(files)
        print("Processing sharp files...")
        processGroupOfPhotos(sharp, "sharp", args.out[0])
        print("Processing questionable files...")
        processGroupOfPhotos(questionable, "questionable", args.out[0])
        print("Processing unsharp files...")
        processGroupOfPhotos(unsharp, "unsharp", args.out[0])
    else:
        processGroupOfPhotos(files, "sharp", args.out[0])

    return 0

def processGroupOfPhotos(photos, prefix, out):
    """
    Does the full work on a group of photos
    """
    print("Grouping files based on EXIF data (slow)...")
    groupedFiles = splitFilesIntoDaysAndCameras(photos, prefix)
    print("Splitting file groups into volumes...")
    volumes = splitGroupsIntoVolumes(groupedFiles)
    print("Copying files over...")
    copyFilesToVolumePaths(out, volumes)


def sortSharpFromUnsharp(files):
    """
    Sorts sharp images from unsharp images

    files:- a list of files to sort
    returns:- sharp, unsharp; lists of files
    """
    sharp = []
    unsharp = []
    questionable = []

    for file in files:
        isSharp = testImageSharpness(file)
        if isSharp == "sharp":
            sharp.append(file)
        elif isSharp == "questionable":
            questionable.append(file)
        else:
            unsharp.append(file)
    
    return sharp, questionable, unsharp


def testImageSharpness(file):
    """
    Tests and image to see if it is sharp

    file:- an image to test for sharpness
    returns:- true if the image is sharp, otherwise false
    """
    global lastIndex
    photo = image_sharpness.Image.fromFile(file)
    wholeImageSharpness = photo.getWholeImageGradientSharpness()
    sharpness = photo.getGradientSharpnessForPrimaryAfPoint(lastIndex)
    if sharpness < 0.5:
        print (file, "- unsharp", sharpness, "/", wholeImageSharpness, " = ", sharpness/wholeImageSharpness)
        return "unsharp"
    elif sharpness >= 0.5 and sharpness < 1.7:
        print (file, "- questionable", sharpness, "/", wholeImageSharpness, " = ", sharpness/wholeImageSharpness)
        return "questionable"
    else:
        print (file, "- sharp", sharpness, "/", wholeImageSharpness, " = ", sharpness/wholeImageSharpness)
        return "sharp"




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



def splitFilesIntoDaysAndCameras(nefFiles, prefix):
    """
    Takes the list of files, and creates a dictionary where they keys are
    the base paths (ie Year/Month/Day/Camera).

    nefFiles:- the full list of NEF files
    returns:- a dictionary of <base path, nef file>
    """
    groupedImages = {}
    for path in nefFiles:
        tags = getTagsFromFile(path)
        basePath = getBasePathFromTags(tags, prefix)
        if basePath not in groupedImages:
            groupedImages[basePath] = []
        groupedImages[basePath].append(path)
        print("\tProcessed metadata for", path)
    return groupedImages

def getTagsFromFile(nefFilePath):
    """
    Retrieve the tags from an NEF file

    nefFilePath:- the path of the file to read
    returns:= a list of the EXIF tags in the file
    """
    tags = []
    with open(nefFilePath, 'rb') as nefFile:
        tags = exifread.process_file(nefFile)
    return tags

def getBasePathFromTags(tags, prefix):
    """
    Uses the 'Image DateTime' and 'Image Model' tags to build a base path
    under which to store images.

    tags:- the tags extracted from the image
    returns:- a partial path
    """
    camera = str(tags[CAMERA_TAG]).replace(" ", "_")
    dateString = str(tags[DATE_TAG])
    dateMatches = DATETIME_RE.match(dateString)
    year = dateMatches.group(1)
    month = dateMatches.group(2)
    day = dateMatches.group(3)

    basePath = os.path.join(prefix, year, month, day, camera)
    return basePath

def splitGroupsIntoVolumes(groupedFiles):
    """
    Takes the list of files grouped into base paths, and splits each group into
    volumes of at most 250 images

    groupedFiles:- a dictionary in the form <base path, file list>
    returns:- a dictionary in the form<base path, list of file lists>
    """
    volumes = {}
    for group in groupedFiles:
        if group not in volumes:
            volumes[group] = []
        numFilesInGroup = len(groupedFiles[group])
        if numFilesInGroup < 250:
            volumes[group].append(groupedFiles[group])
        else:
            numVolumes = int((numFilesInGroup / 250)) + 1
            for volumeIndex in range(1, numVolumes):
                startIndex = (volumeIndex - 1) * 250
                endIndex = startIndex + 250
                if volumeIndex == 1:
                    volumes[group].append(groupedFiles[group][:endIndex])
                elif volumeIndex == numVolumes:
                    volumes[group].append(groupedFiles[group][startIndex:])
                else:
                    volumes[group].append(groupedFiles[group][startIndex:endIndex])
    return volumes

def copyFilesToVolumePaths(outDir, volumes):
    """
    Iterates through the collection of volumes and does the actual
    file copying

    outDir:- the base out path
    volumes:- the collection of files grouped by day and camera, and split into volumes
    """
    for group in volumes:
        baseOutPath = os.path.join(outDir, group)
        volumeIndex = 1
        for volume in volumes[group]:
            volumeString = str(volumeIndex)
            volumePath = os.path.join(baseOutPath, volumeString)
            os.makedirs(volumePath, exist_ok=True)
            for photo in volume:
                photoBaseName = os.path.basename(photo)
                photoOutPath = os.path.join(volumePath, photoBaseName)
                print("\tCopy", photo, "to", photoOutPath)
                shutil.copyfile(photo, photoOutPath)
            volumeIndex += 1

if __name__ == "__main__":
    parser = python_batch_processing.StandardisedArguments.create_basic_parser(
        "Import digital photos from a memory card into a nice structure")
    parser = image_sharpness.StandardisedArguments.add_sharpness_arguments(parser)
    arguments = parser.parse_args()
    main(arguments)
