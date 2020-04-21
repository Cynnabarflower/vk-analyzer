import json


def open_coordinates_file(f_name="coordinates.txt"):
    """
    Maidzhe Alexandra
    Opens and deserializes a file into a dict.
    :param f_name:
    :return:
    """
    with open(f_name, encoding="utf-8", mode="r") as f:
        allcoordinates = json.load(f)
    f.close()
    return allcoordinates

def polyregions(verts, coord):
    """
    Maidzhe Alexandra
    Builds a polygon out of the coordinates of regions's borders;
    Check if the given coordinate is inside the polygon.
    :param verts:
    :param coord:
    :return:
    """
    from matplotlib.path import Path
    path = Path(verts) #Path connects all the points of given coordinates and returns a polygon
    l = path.contains_point(coord)
    return l


def region(allcoordinates, coordinates):
    """
    Maidzhe Alexandra
    Goes through regions' borders and passes
    the coordinates to the polyregions function.
    Finds the name of the region
    :param allcoordinates:
    :param coordinates:
    :return:
    """
    p = False  #auxilary variable to check if the region was found or not
    n = 0
    while n <= len(allcoordinates)-1 and not p:
        name = allcoordinates[n]['name']
        a = 0
        while a <= len(allcoordinates[n]['coordinates'])-1:
            p = polyregions(verts1, coordinates)
            a += 1
        n += 1
        if p:
            return name

#***********************************************************************
#region_coordinates = open_coordinates_file()
#nome = region(region_coordinates, coordinates)
#import this file and write the two lines before this one.