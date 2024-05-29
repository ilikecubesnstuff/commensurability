---
title: 'commensurability - a python package for classifying astronomical orbits based on their toroid volume'
tags:
  - Python

authors:
  - name: Subhadeep Sarkar
    corresponding: true
    affiliation: "1"
    orcid: 0000-0000-0000-0000
  - name: Michael S. Petersen
    affiliation: "1"
    orcid: 0000-0003-1517-3935
affiliations:
 - name: University of Edinburgh
   index: 1
date: 
bibliography: paper.bib

# Arxiv information
arxiv-doi: 
---

# Summary

Stars like our Sun orbit the centre of our Milky Way galaxy. Over many orbits in the disc of the galaxy, the Sun will (hypothetically) probe every point in a 3d toroid defined by a minimum/maximum radius and minimum/maximum height above the midplane. However, a special class of stars are on orbits that repeat their tracks with every revolution around the galactic centre, and therefore only probe a small sub-volume of the toroid. These orbits are called ``commensurate". 

To study the orbital content of galaxies, astronomers will often use models for galaxies that allow for integration of orbits within the model potential. The integration results in a time series of positions (e.g. \[x-y-z\]) for the orbit that can then be analyzed to produce a classification. Complicating this picture, in potentials evolving with time, a new frequency emerges: the pattern frequency of the evolution. The evolution of the potential might be the rotation of a galactic bar, the formation or dissolution of spiral arms, the growth of the galaxy, or the interaction of a satellite galaxy. Orbits that are commensurate with the pattern frequency are particularly important in galactic dynamics as they experience the same force fluctuations during every revolution: this causes changes to the typically conserved quantities of orbits (e.g. energy and angular momentum).

Given their importance, astronomers have developed techniques to identify commensurate orbits. One technique is ``orbit tesselation'', which seeems to estimate the (sub-)volume of the toroid traversed by an orbit [@Petersen.Weinberg.Katz.2021]. Orbit tessellation aims to pick out commensurate orbits with relatively short orbit integration times, as well as pick out commensurabilities in cases where the kinematic frequencies need not stay constant (such as in a potential with multiple pattern frequencies from multiple causes).

The python package presented here, commensurability, provides a straightforward python interface and connection to powerful tools for modeling potentials to estimate the volume of a toroid that a given orbit fills. 


# Statement of need

The technique of measuring orbit volumes has previously been used to classify orbits in 2d in both fixed and evolving potentials, revealing families of commensurate orbits that are critical for galactic evolution [@Petersen.Weinberg.Katz.2021]. However, the technique had not (1) been extended to 3d, and (2) did not have a user-friendly python interface. The commensurability package solves both problems, and provides a valuable interface to three leading galactic dynamics packages.

More generally, classifying orbits in model galaxies, let alone in models that evolve with time, is a non-trivial task. The primary method to classify orbits in galaxies relies on frequency analysis, such as with the superfreq [@superfreq.paper] or naif [@naif.paper] codes. While frequency analysis is a useful tool, ambiguity in the classification remains. Frequency analysis relies on the stability of the frequencies of an orbit, which may miss both short-lived families as well as smoothly-changing frequencies. Orbit tesselation avoid these pitfalls. The goal of extending an orbit classification scheme with orbit tesselation is to both improve on fundamental frequency classifications, and build an independent classification scheme that can operate on orbits run in self-consistent simulations.

Additionally, computing the orbit volume provides an opportunity to efficiently search the model potential space for unique orbits. By creating a measure that is defined at all points in phase space (typically defined in the position and velocity of a radial extreme), one can search a model potential for commensurate orbits using optimisation techniques.

 ![An example diagnostic from commensurability, where an orbit is selected from a map of toroid volumes (left panel). In the map, orbits with small volumes are dark colored. The ``tracks'', including the curve highlighted in red, are families of orbits. The orbits are all in the frame of a rotating bar; the shape traced by this particular orbit in x-y position space (right panel) is a characteristic bar orbit, drawn from a point on the red curve. \label{fig:x1orbit}](figures/track_eye.png)

# Features and dependencies

There are a number of notable features in commensurability. First, the user interface. A class named Analysis enables exploration of the potential via an interactive matplotlib [@matplotlib.paper] figure. Given a map of the measure of the toroidal volume as a function of phase space (for instance in x-vy), the user can visually select regions of interest, and the interactive plot will update with the x-y-z time series of the orbit. Further, Analysis objects include methods for serialization and deserialization in HDF5 format [@hdf5.paper], which saves significant computational expense after having computed orbit volumes. 

Second, commensurability has dependencies that allow for interoperability with other galactic dynamics packages. The python package [pidgey](https://github.com/ilikecubesnstuff/pidgey) asserts a uniform interface to three major orbit integration packages: agama [@agama.paper], gala [@gala.paper], and galpy [@galpy.paper]. Pidgey can be used as a standalone package, and provides a framework that makes extending orbit integration with other packages trivial.  The coordinates for orbits are implemented as astropy [@astropy.paper] SkyCoord objects, a format familiar to most astronomers. The commensurability package also depends on [iext](https://github.com/ilikecubesnstuff/iext), which provides the framework that delineates the dependency injections for a class. This enables pidgey to operate in the absence of a complete suite of orbit integration packages; the user need only have one of agama, gala, or galpy installed to use commensurability (but may have all three).

Third, commensurability implements mathematical and computational improvements over early versions of orbit tesselation-based classification [@Petersen.Weinberg.Katz.2021]. Several normalizations now exist for the toroid volume, computed after trimming insignificant simplices based on their axis ratio. The default normalization for the orbit volume is the convex hull of four rotated copies of the points around the z-axis. The rotated copies protect against missing orbits that only span a small range of azimuth about the z-axis. The convex hull is computed using QHull [@qhull.paper] as implemented in scipy [@scipy.paper]. Additionally, a subpackage included in commensurability, called tessellation, implements n-dimensional tesselation and processing over the volumes. While only two and three-dimensional tesselations are used in commensurability, this subpackage could be used as a standalone tesselation method in higher dimensions.


# Provided example workflows and usage

To help users begin using the software in their own research, we provide a [readthedocs](https://commensurability.readthedocs.io) page with a [quickstart](https://commensurability.readthedocs.io/en/latest/quickstart/) that includes pip-based installation instructions, as well as examples drawn from real scientific applications. First, we feature a demonstration of orbital classification in a model of a [rotating bar](https://commensurability.readthedocs.io/en/latest/tessellation/usage/analysis/rotating_bar/), including how to perform the orbit integration using various backends from pidgey. \autoref{fig:x1orbit} shows the results from one demonstration orbit in the rotating bar documentation, where a bar orbit is detected through a tracing a curve of vanishing toroid volume.

Second, we demonstrate orbital classification in the [solar neighborhood](https://commensurability.readthedocs.io/en/latest/tessellation/usage/analysis/solar_neighborhood/) for a standard Milky Way potential, revealing a rich dynamical structure of commensurate orbits. 

The readthedocs page also hosts an extensive API reference, with all code adhering to [the Black code style](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html) for ease of readability.


# Acknowledgements

We thank Aneesh Naik and Eugene Vasiliev for discussions regarding early versions of the software.

# References