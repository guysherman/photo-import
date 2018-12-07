# pylint: disable=C0103
"""
An object which has functions to test whether an image is sharp
"""
import os
import exifread
import numpy as np
import rawpy
from PIL import Image as pilImage
import imageio

AfPointLookup = [[0,0],
[3015,2014],
[3015,1759],
[3015,1504],
[3015,2269],
[3015,2524],
[3249,2014],
[3249,1759],
[3249,1504],
[3249,2269],
[3249,2524],
[2781,2014],
[2781,1759],
[2781,1504],
[2781,2269],
[2781,2524],
[3483,2014],
[3483,1674],
[3483,2354],
[3717,2014],
[3717,1674],
[3717,2354],
[3951,2014],
[3951,1674],
[3951,2354],
[4185,2014],
[4185,1674],
[4185,2354],
[2547,2014],
[2547,1674],
[2547,2354],
[2313,2014],
[2313,1674],
[2313,2354],
[2079,2014],
[2079,1674],
[2079,2354],
[1845,2014],
[1845,1674],
[1845,2354]]

AFINFO2_TAG = "MakerNote AFInfo2"

class Image:
    """
    An object which has functions to test whether an image is sharp
    """
    def __init__(self, filename):
        """
        Constructs a new Image object which extracts the rgb, grayscale and gradient layers of itself, 
        and grabs the AFInfo2 header from the image

        filename:- the file to load
        """
        with rawpy.imread(filename) as rawImage:
            self.rgbImage = rawImage.postprocess()
            lumoImage = pilImage.fromarray(self.rgbImage).convert('L')
            
            self.lumoImage = np.asarray(lumoImage, dtype=np.int32)
            self.lumoGradient = gradientFromLumo(lumoImage)
        

        tags = getTagsFromFile(filename)
        self.AFInfo2 = tags[AFINFO2_TAG]

    def getPrimaryAfPointIndex(self, lastIndex):
        """
        Returns the index of the primary af point, or the passed-in index if there is no primary

        lastIndex:- the previous index retrieved. This allows the caller to reuse the last focus point
        """
        index = self.AFInfo2.values[7]
        if index == 0:
            index = lastIndex
        return index
    
    
    def getPrimaryAfPointTile(self, layer, lastIndex):
        """
        Returns the tile form the primary af point for the image

        layer:- as string with one of 'rgb', 'l' or 'grad', selects which layer the tile comes from
        returns:- a numpy array with the requested tile
        """
        return self.getAfPointTile(self.getPrimaryAfPointIndex(lastIndex), layer)
    
    def getAfPointTile(self, afPointIndex, layer):
        """
        Returns the tile corresponding to the primary AF Point for the image, from the selected layer

        afPointIndex:- the index of the AF point to retrieve the tile for
        layer:- as string with one of 'rgb', 'l' or 'grad', selects which layer the tile comes from
        returns:- a numpy array with the requested tile
        """
        top, bottom, left, right = determineAfPointBox(afPointIndex)
        if layer == 'rgb':
            return self.rgbImage[top:bottom, left:right, :]
        elif layer == 'l':
            return self.lumoImage[top:bottom, left:right]
        elif layer == 'grad':
            return self.lumoGradient[top:bottom, left:right]
        else:
            return np.asarry([[0]], dtype=np.int32)

    def getLayer(self, layer):
        """
        Gets the given layer from the image

        layer:- as string with one of 'rgb', 'l' or 'grad', selects which layer to retrieve
        """
        if layer == 'rgb':
            return self.rgbImage
        elif layer == 'l':
            return self.lumoImage
        elif layer == 'grad':
            return self.lumoGradient
        else:
            return np.asarry([[0]], dtype=np.int32)
    
    def getWholeImageGradientSharpness(self):
        """
        Average the entire image gradient to give overall 'sharpness'
        """
        return np.average(self.lumoGradient)

    def getGradientSharpnessForPrimaryAfPoint(self, lastIndex):
        """
        Average the primary af point tile gradient to give 'sharpness' of the tile
        """
        return np.average(self.getPrimaryAfPointTile('grad', lastIndex))

    def getWholeImageVarianceSharpness(self):
        """
        Get variance measure for whole image
        """
        return self.getVarianceSharpnessForImage(self.lumoImage)
    
    
    def getVarianceSharpnessForImage(self, image):
        """
        Uses the variance method (http://www.csl.cornell.edu/~cbatten/pdfs/batten-image-processing-sem-slides-scanning2001.pdf)
        to calculate image sharpness
        """
        normImage = image / 255
        meanIntensity = np.average(normImage)
        diff = normImage - meanIntensity
        diffSq = diff**2
        sharpnessVector = np.add.reduce(diffSq)
        sharpness = np.add.reduce(sharpnessVector) / normImage.size
        return sharpness

    def getVarianceSharpnessForPrimaryAfPoint(self, lastIndex):
        """
        Get variance sharpness for primary af point image
        """
        afImage = self.getPrimaryAfPointTile('l', lastIndex)
        return self.getVarianceSharpnessForImage(afImage)




def fromFile(filename):
    return Image(filename)


def gradientFromLumo(lumoImage):
    """
    Converts a grayscale image into the 2d gradient of that image

    lumoImage:- a grayscale image
    returns:- a numpy array containing the gradient data
    """
    luminosityData = np.asarray(lumoImage, dtype=np.int32)
    yGradient, xGradient = np.gradient(luminosityData)
    normGradient = np.sqrt(xGradient**2, yGradient**2)
    return normGradient


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

def determineAfPointBox(afPointIndex):
    """
    Extracts the coordinates of the primary AF point

    file:- the raw image to process
    returns: = top, bottom, left, right
    """
    afPointCentre = AfPointLookup[afPointIndex]
    top = afPointCentre[1] - 128
    bottom = afPointCentre[1] + 127
    left = afPointCentre[0] - 128
    right = afPointCentre[0] + 127
    return top, bottom, left, right
