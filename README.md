# Galaxy2

[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)]
(https://github.com/samhollenbach/Galaxy2/LICENSE)
[![Release Version](https://img.shields.io/badge/release-2.1-red.svg)](https://github.com/Tencent/mars/releases)


![Example](resources/galaxy2.gif "Example Galaxy shown with the Reader.py with 400 particles")

**Visualizing a single galaxy with 400 particles in the Reader.py program** 

## Background

This simulation began as a open ended project for my Modern Astronomy course as a freshman at Macalester College. The first generation (Galaxy_v1) could only be visualized in 2D and had a very rudimentary Dark Matter approximation, as well as being very inefficient in many calculations. 

Galaxy_v1 can be found [here](https://github.com/samhollenbach/Galaxy)

## Features of Galaxy2

Galaxy2 has been drasticly improved in simulation accuracy, code effciency, and visualization.


Notable features of v2.1:

* [Navarro-Frenk-White Dark Matter Profile](https://arxiv.org/abs/astro-ph/9508025) integration
* Dark Matter analysis mode, to quickly determine how accurate the NFW profile is with specified constants
* [3D visualization](https://github.com/samhollenbach/Galaxy2/blob/master/Reader.py) using [matplotlib](http://matplotlib.org/)
* Parallel processing ability using [joblib](https://pythonhosted.org/joblib/)
* Improved code speed and readability

## Creating your own galaxy

The format for creating a galaxy in Galaxy2 is a very simple 4 steps:

1. Create your galaxy with specified spiral disk size, position, and star number. The galaxy must have an ID to differentiate between other galaxies for color visualization.*
```python
milky_way = Galaxy(galaxy_width, galaxy_height, posX, posY, posZ, starNum, id)
```

2. Sets the peculiar velocity of your galaxy (for interaction between multiple galaxies).
```python
milky_way.vel = np.array([velocityX, velocityY, velocityZ])
```

3. Randomly distributes the stars in your galaxy based on distance from galactic center.
```python
milky_way.setstardistribution() 
```

4. Add this galaxy to the simulation
```python
galaxies.append(milky_way)
```

There are two built in methods for creating 1 or 2 galaxies:
```python
single_galaxy()
```
and
```python
double_galaxy()
```
These methods can be found in the [SimMain.py file](https://github.com/samhollenbach/Galaxy2/blob/master/SimMain.py)

## The sim_data file

The first line of the data file is always
```python
HEAD:{Number of Galaxies},{Total Particle Number}
```
This lets the reader know how many particles and galaxies to expect so it can draw the labels on the screen.


The subsequent lines start with the iteration number, and for each iteration there is a line for every particle in the simulation. This means the total number of lines in the file will be **{Total Iterations}x{Total Particles}+1**

The format for each iteration line is
```python
{Iteration},{Particle_X},{Particle_Y},{Particle_Z},{Source_Galaxy_ID}
```

The example sim_data file is [here](https://github.com/samhollenbach/Galaxy2/blob/master/sim_data.txt)

See the Reader.py for more info on how to parse the datafile.


Please contact me at shollenb@macalester.edu if you have any quesitons or inquiries.
