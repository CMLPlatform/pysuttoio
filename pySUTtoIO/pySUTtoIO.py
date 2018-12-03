# -*- coding: utf-8 -*-

"""Main module."""

import pySUTtoIO.transformation_model_0 as tm0
import pySUTtoIO.transformation_model_b as tmb


def tm0(self, sut, env_extensions, make_secondary=False):

    tm0 = tm0.TransformationModel0(sut, env_extensions, make_secondary)

    return tm0

def tmb(self, sut, env_extensions, make_secondary=False):

    tmb = tmb.TransformationModelb(sut, env_extensions, make_secondary)

    return tmb

