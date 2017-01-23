# Galaxy2

[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)]
(https://github.com/samhollenbach/Galaxy2/LICENSE)
[![Release Version](https://img.shields.io/badge/release-2.1-red.svg)](https://github.com/Tencent/mars/releases)

## Background

This is a project created by Sam Hollenbach as an independent research project at Macalester College.

The simulation began as a open ended project for my Modern Astronomy course during as a freshman. The first generation (Galaxy_v1) could only be visualized in 2D and had a very rudimentary Dark Matter approximation, as well as being very inefficient doing many calculations. 

Galaxy_v1 can be found at [here](https://github.com/samhollenbach/Galaxy)

## Features of Galaxy2

Galaxy2 has been drasticly improved in simulation accuracy, code effciency, and visualization.


Notable features of v2.1:

-[NFW Dark Matter Profile integration](https://en.wikipedia.org/wiki/Navarro%E2%80%93Frenk%E2%80%93White_profile)

-Dark Matter analysis mode, to quickly determine how accurate the NFW profile is with specified constants

-[3D visualization](https://github.com/samhollenbach/Galaxy2/blob/master/Reader.py) using the Python library [matplotlib](http://matplotlib.org/)

-Parallel processing ability using the Python library [joblib](https://pythonhosted.org/joblib/)

-All around improved code speed and readability

## Creating your own galaxy

The format for creating a galaxy in Galaxy2 is very simple:

```python
#Create your galaxy with specified spiral disk size, position, and star number
#Must have an id to differentiate between other galaxies
milky_way = Galaxy(galaxy_width, galaxy_height, posX, posY, posZ, starNum, id)

#Sets the velocity of your galaxy (mainly for interaction between multiple galaxies)
milky_way.vel = np.array([velocityX, velocityY, velocityZ])

#Randomly distributes the stars in your galaxy 
milky_way.setstardistribution() 

#Add this galaxy
galaxies.append(milky_way)
```

You can find the 
```python
single_galaxy()
```
and
```python
double_galaxy()
```
methods in the [SimMain.py file](https://github.com/samhollenbach/Galaxy2/blob/master/SimMain.py), which follow this same format.

Contact me at shollenb@macalester.edu if you have any quesitons
