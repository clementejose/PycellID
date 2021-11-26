# !/usr/bin/env python

# -*- coding: utf-8 -*-

# This file is part of the
#   PyCellID Project (
#     https://github.com/pyCellID,
#     https://github.com/darksideoftheshmoo
# ).
# Copyright (c) 2021. Clemente, Jose
# License: MIT
#   Full Text: https://github.com/pyCellID/pyCellID/blob/main/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""Merge and analyze tables of characteristics of cells and find images."""

# =============================================================================
# IMPORTS
# =============================================================================

import warnings
from pathlib import Path

import attr

import matplotlib.pyplot as plt

from pycellid import images as img
from pycellid.io import merge_tables


# =============================================================================
# CellData Class
# =============================================================================


@attr.s(repr=False)
class CellData(object):
    """Collapse your data into a single data frame.

    Recursively inspect the path, create a unique identifier per cell,
    and inspect related images.

    Parameters
    ----------
    path:
        global path from output ``cellID`` tables.

    Return
    ------
        A dataframe ``cellID``.

    * to use:

    >>> from pycellid.core import CellData
    >>> df = CellData(
        path = '../my_experiment'
    )

    Other Parameters
    ----------------
    name_data:
        srt() file name to finde each table data.
    name_meta_data:
        srt() file name to finde tables metadata or mapping_tags
    verbose:
        bool, True to print in realtime pipeline

    """

    path = attr.ib(validator=attr.validators.instance_of(str))

    # : Starting with ``*`` will perform a recursive search on each string.
    name_data = attr.ib(
        validator=attr.validators.instance_of(str), default="out_all"
    )

    # : Starting with ``*`` will perform a recursive search on each string.
    name_meta_data = attr.ib(
        validator=attr.validators.instance_of(str), default="*mapping"
    )

    @path.validator
    def _check_path(self, attribute, value):
        if not Path(value).exists():
            raise FileNotFoundError(f"Path < {value} > not exist")

    @property
    def df(self):
        """Return a copy of the underlying Dataframe.

        This property cosntruct the data tables.
        """
        if "_df" not in vars(self):
            self._df = merge_tables(
                path=self.path,
                n_data=self.name_data,
                n_mdata=self.name_meta_data,
            )
        return self._df.copy()

    @property
    def plot(self):
        """Represent set of ``cells_image`` or numerical data.

        For ``cimage`` method you must specify an identifier id={}.
        """
        return CellsPloter(self)

    def __getattr__(self, a):
        """
        Is called when the default attribute access fails (AttributeError).

        getattr(x, y) <==> x.__getattr__(y) <==> getattr(x, y).
        """
        return getattr(self.df, a)

    def __getitem__(self, k):
        """
        Call to implement evaluation of self[key].

        x[k] <=> x.__getitem__(k).
        """
        return self.df.__getitem__(k)

    def __iter__(self):
        """
        Call when an iterator is required for a container.

        iter(x) <=> x.__iter__().
        """
        return iter(self.df)

    def __len__(self):
        """
        Call to implement the built-in function len().

        len(x) <=> x.__len__().
        """
        return len(self.df)

    def __repr__(self):
        """
        Compute the “official” string representation of an object.

        repr(x) <=> x.__repr__().
        """
        return f"CellData(data={hex(id(self.df))})"

    def __repr_html__(self):
        """Print a rich HTML version of your object."""
        return self.df._repr_html_()

    def __setitem__(self, key, values):
        """Call to implement assignment to self[key]."""
        self._df[key] = values


# =============================================================================
# CellsPloter Class
# =============================================================================


@attr.s(repr=False)
class CellsPloter:
    """
    Accessor to plotter class.

    Create a representation of each cell within a grid, inspect an entire
    image or create a snippet of a single cell.
    We provide a wrapper of the same pandas methods for plotting.

    Returns
    -------
    axes to plot

    Attributes
    ----------
    cells_image:
        Matrix of cells
    cimage:
        single cell representation.
    """

    cells = attr.ib()

    def __repr__(self):
        """
        Compute the “official” string representation of an object.

        repr(x) <=> x.__repr__().
        """
        return f"CellsPloter(cells={hex(id(self.cells))})"

    def __call__(self, kind="cells_image", **kwargs):
        """
        When the instance is “called” as a function.

        type(x).__call__(x, arg1, ...).
        """
        method = getattr(self, kind, None)
        if method is None:
            method = getattr(self.cells._df.plot, kind)
        return method(**kwargs)

    def __getattr__(self, a):
        """
        Is called when the default attribute access fails (AttributeError).

        getattr(x, y) <==> x.__getattr__(y) <==> getattr(x, y).
        """
        return getattr(self.cells._df.plot, a)

    def cells_image(self, array_img_kws=None, imshow_kws=None, ax=None):
        """Representation of a set of cells.

        By default it represents a 4 X 4 matrix chosen at random.

        Returns
        -------
        ax to plot or figure.

        Other Parameters
        ----------------
        array_img_kws : dict.
            Set the pycellid.images.img_array parameters.
            n : number of cells.
            channles : "TFP" or another that you have encoded.

        imshow_kws : dict
            If you use matplotlib set equal to plt.imshow.

        ax:
            Use your axes to plot.
        """
        data_c = self.cells

        ax = plt.gca() if ax is None else ax

        imshow_kws = {} if imshow_kws is None else imshow_kws
        array_img_kws = {} if array_img_kws is None else array_img_kws

        imshow_kws.setdefault("cmap", "Greys")

        arr_c = img.array_img(data=data_c, path=data_c.path, **array_img_kws)

        ax.imshow(arr_c, **imshow_kws)
        ax.axis("off")
        return ax

    def cimage(self, idtfer, box_img_kws=None, imshow_kws=None, ax=None):
        """Representation of a sigle cell or image.

        Identifier ``idtfer`` is required. Reference a valid image or position.
        By default, an image with a size of (1392 X 1040)px will be rendered.
        Use the arguments of box_img_kws to choose as you like.

        Params
        ------
        idtfer : path or dict.
            path to an image file
            dict = {
                "channel":str,
                "UCID":int,
                "t_frame":int,
            }

        Returns
        -------
        ax to plot or figure.

        Other Parameters
        ----------------
        box_img_kws : dict.
            Set the pycellid.images.box_img parameters.
            im : numpy.array.
                A full fluorescence microscopy image.
            x_pos : int.
                x-coordinate of the center of the cell of interest.
            y_pos : int.
                x-coordinate of the center of the cell of interest.
            radius : int.
                lenght (in px) between the center of the image and each edge.
                defoult = 90.
            mark_center: bool
                mark a black point.
                defoult = False.

        imshow_kws : dict
            If you use matplotlib set equal to plt.imshow.
        ax:
            Use your axes to plot.
        """
        data_c = self.cells

        ax = plt.gca() if ax is None else ax

        imshow_kws = {} if imshow_kws is None else imshow_kws
        box_img_kws = {} if box_img_kws is None else box_img_kws

        imshow_kws.setdefault("cmap", "Greys")

        if isinstance(idtfer, dict):
            ucid = idtfer["ucid"]
            t_frame = idtfer["t_frame"]
            try:
                [[x, y]] = data_c[
                    (data_c.ucid == ucid) & (data_c.t_frame == t_frame)
                ][["xpos", "ypos"]].values.tolist()
                r = 90
            except ValueError:
                x, y, r = int(1392 / 2), int(1040 / 2), int(1040 / 2)
                message = "not match ucid and t_frame. See picture!"
                warnings.warn(message)

            idtfer = img.img_name(data_c.path, **idtfer)

        else:
            x, y, r = int(1392 / 2), int(1040 / 2), int(1040 / 2)

        box_img_kws.setdefault("x_pos", x)
        box_img_kws.setdefault("y_pos", y)
        box_img_kws.setdefault("radius", r)

        arr = plt.imread(idtfer)
        arr_c = img.box_img(im=arr, **box_img_kws)

        ax.imshow(arr_c, **imshow_kws)
        ax.axis("off")
        return ax
