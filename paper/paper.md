---
title: 'commensurability: a Python package for classifying astronomical orbits based on their toroid volume'
tags:
  - Python
  - astronomy
  - dynamics
  - galactic dynamics
  - milky way
  - tessellation

authors:
  - name: Subhadeep Sarkar
    corresponding: true
    affiliation: "1"
    orcid: 0009-0006-9454-5141
  - name: Michael S. Petersen
    affiliation: "1"
    orcid: 0000-0003-1517-3935
affiliations:
 - name: Insitute for Astronomy, University of Edinburgh
   index: 1
date: 
bibliography: paper.bib

# Arxiv information
arxiv-doi: 
---

# Summary

Stars like our Sun orbit the center of our Milky Way galaxy. Over many orbits in the stellar disk of the galaxy, a star will (hypothetically) probe every point in a 3D toroid defined by a minimum/maximum radius and minimum/maximum height above the midplane. However, there are special classes of orbits that repeat their tracks with every revolution around the Galactic center, and therefore only probe a small sub-volume of the toroid. This property stems from low-integer orbital frequency ratios -- commensurate frequencies -- and such orbits are referred to as satisfying a "commensurability".

To study the orbital content of galaxies, astronomers often use models for galaxies that allow for the integration of orbits within the model galaxy's potential. The integration results in a time series of positions (e.g. $x,y,z$) for the orbit that can then be analyzed to produce a classification. Complicating this picture, potentials evolving with time introduce a new frequency: the pattern frequency of the evolution. The evolution of the potential might be sourced by the rotation of a galactic bar, the formation or dissolution of spiral arms, the growth of the galaxy, or the interaction with a satellite galaxy. Orbits that are commensurate with the pattern frequency are particularly important in galactic dynamics as they experience the same force fluctuations during every revolution: this causes changes to the typically conserved quantities of orbits (e.g. energy and angular momentum).

Given their importance, astronomers have developed techniques to identify commensurate orbits. One technique is “orbit tessellation”, which estimates the (sub-)volume of the toroid traversed by an orbit [@Petersen.Weinberg.Katz.2021]. The method of orbit tessellation aims to pick out commensurate orbits over relatively short orbit integration times, as well as pick out commensurabilities in cases where the kinematic frequencies need not stay constant (such as in a potential with multiple pattern frequencies from multiple causes).

The Python package presented here, `commensurability`, provides a straightforward Python framework and connection to powerful tools for modeling potentials to estimate the volume of a toroid that a given orbit fills. 


# Statement of need

The technique of measuring orbit volumes has previously been used to classify orbits in 2D in both fixed and evolving potentials, revealing families of commensurate orbits that are critical for galactic evolution [@Petersen.Weinberg.Katz.2021]. However, the technique had not (1) been extended to 3D, and (2) did not have a user-friendly Python interface. The `commensurability` package solves both problems and provides interoperability with three leading galactic dynamics packages to accomplish the underlying orbit integrations.

More generally, classifying orbits in model galaxies, let alone in models that evolve with time, is a non-trivial task. The primary method to classify orbits in galaxies relies on frequency analysis, such as with the superfreq [@superfreq.paper] or naif [@naif.paper] codes. While frequency analysis is a useful tool, there remains ambiguity in the classification of commensurate orbits over short durations, or while frequencies change. Frequency analysis relies on the stability of the frequencies of an orbit, which may miss short-lived families and smoothly changing frequencies. Orbit tessellation avoids these pitfalls by estimating the volume of the toroid the orbit would traverse in the long-time limit, even if frequencies are changing over time. Orbit tessellation improves on fundamental frequency classifications, but also exists as an independent orbit classification scheme that can operate on orbits run in self-consistent simulations.

Additionally, computing the orbit volume provides an opportunity to efficiently search the model potential space for distinct orbital families. By creating a measure that is defined at all points in phase space (typically defined in the position and velocity of a radial extreme), one can search a model potential for commensurate orbits using optimization techniques.

 ![An example diagnostic from commensurability, where an orbit is selected from a map of toroid volumes in radial position $x$ and tangential velocity $v_y$ (left panel). In the map, orbits with small measures are dark-colored. The “tracks”, including the curve highlighted in red, are families of orbits. The orbits are all in the frame of a rotating bar; the shape traced by this particular orbit in x-y position space (right panel) is a characteristic bar orbit, drawn from a point on the red curve. \label{fig:x1orbit}](figures/track_eye.png)


# Features and dependencies

`commensurability` provides several notable features, with an emphasis on extensibility and compatibility with existing code.

`commensurability` defines a framework for analyzing potentials in its “analysis” objects. “TessellationAnalysis” uses [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) to efficiently compute the normalized toroidal volumes of orbits, or evaluate orbit “measures”. Analysis objects are equipped with interactive matplotlib [@matplotlib.paper] figures displaying a map of orbit measures as a function of phase space (for instance in position-velocity $x,v_y$; \autoref{fig:x1orbit}). A user can explore the potential by visually selecting regions of interest, and the interactive plot will update with the $x,y,z$ time series of the orbit. Since evaluating a large number of orbits can require significant computational power, analysis objects also include serialization and deserialization methods using the HDF5 format [@hdf5.paper]. Although TessellationAnalysis objects focus on orbit tessellation specifically, the analysis framework to determine commensurability can be easily extended to any orbit evaluation method.

`commensurability` provides a subpackage called tessellation that implements mathematical and computational improvements over early versions of orbit tessellation-based classification [@Petersen.Weinberg.Katz.2021]. While only two- and three-dimensional orbits are evaluated in commensurability, the subpackage implements a general N-dimensional evaluation algorithm. Several normalizations are provided for the toroid volume, computed after trimming insignificant simplices based on their axis ratio, and new normalizations can be defined easily. The default normalization in 3D for the orbit volume is the convex hull of four rotated copies of the points around the $z$-axis (the rotation axis of the model galaxy). The rotated copies protect against missing orbits that only span a small range of azimuth about the $z$-axis. The convex hull is computed using QHull [@qhull.paper] as implemented in scipy [@scipy.paper]. This subpackage can be used for its orbit evaluation function independent of commensurability.

`commensurability` depends on the Python package [pidgey](https://github.com/ilikecubesnstuff/pidgey) for orbit integration. Pidgey is a standalone package that asserts a uniform interface to three major galactic dynamics packages—agama [@agama.paper], gala [@gala.paper], and galpy [@galpy.paper]—and its interface can be extended to more packages trivially. Pidgey uses astropy [@astropy.paper] SkyCoord objects to store orbit coordinates, a format familiar to most astronomers. Pidgey depends on [iext](https://github.com/ilikecubesnstuff/iext), a defensive framework for extending the dependencies associated with a class without requiring the dependencies to be present. This enables pidgey to operate in the absence of a complete suite of orbit integration packages; the user need only have one of agama, gala, or galpy installed to use commensurability (but may have all three).


# Provided example workflows and usage

To help users begin using the software in their research, we provide a [readthedocs](https://commensurability.readthedocs.io) page with pip-based [installation](https://commensurability.readthedocs.io/en/stable/tessellation/usage/) instructions, a [quickstart](https://commensurability.readthedocs.io/en/latest/quickstart/), and examples drawn from real scientific applications. First, we feature a demonstration of orbital classification in a model of a [rotating bar](https://commensurability.readthedocs.io/en/latest/tessellation/usage/analysis/rotating_bar/), where a bar orbit is detected by tracing a curve of vanishing toroid volume as shown in \autoref{fig:x1orbit}. Second, we demonstrate orbital classification in the [solar neighborhood](https://commensurability.readthedocs.io/en/latest/tessellation/usage/analysis/solar_neighborhood/) for a standard Milky Way potential, revealing a rich dynamical structure of commensurate orbits.

The readthedocs page also hosts an extensive API reference, with all code adhering to [the Black code style](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html) for ease of readability.


# Acknowledgements

We thank Aneesh Naik and Eugene Vasiliev for discussions regarding early versions of the software.


# References