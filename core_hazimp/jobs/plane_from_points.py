# -*- coding: utf-8 -*-

"""
Given a set of xyz values estimate z for new x, y pairs.
"""

import numpy


class Plane(object):
    """
    A plane, defined by best fit to a set of points.
    Designed to estimate a z value.
    """

    def __init__(self, xyz):

        # Shift the x, y and x values to be around the origin
        xyz_offset = numpy.mean(xyz, axis=0)
        xyz_origin = xyz - xyz_offset

        coef = fit_plane_svd(xyz_origin)

        self.coef = coef
        self.x_offset = xyz_offset[0]
        self.y_offset = xyz_offset[1]
        self.z_offset = xyz_offset[2]

    def estimate_z(self, x, y):
        """
        Giving x and y arrays, estimate the z array.
        """
        # shift the x and y values to be around the origin
        x_origin = x - self.x_offset
        y_origin = y - self.y_offset

        z_origin = ((self.coef[0] * x_origin + self.coef[1] * y_origin) /
                    -(self.coef[2]))

        # Remove the z offset
        z = z_origin + self.z_offset
        return z


def fit_plane_svd(xyz):
    """
    Calculates a plane that passes thru the origin
    representing a best fit to the xyz values.

    (v[0]x + v[1]y)/ - v[2] = z
    v[3] = ??

    # Code from;
    # http://stackoverflow.com/questions/15959411/
    # fit-points-to-a-plane-algorithms-how-to-iterpret-results
    """
    [rows, _] = xyz.shape
    p = (numpy.ones((rows, 1)))
    ab = numpy.hstack([xyz, p])
    [_, _, vh] = numpy.linalg.svd(ab)
    v = vh.conj().transpose()

    # (v[0]x + v[1]y)/-v[2] = z
    return v[:, -1]

#-------------------------------------------------------------
if __name__ == "__main__":
    pass
