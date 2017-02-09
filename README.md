# Galaxy2

[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)]
(https://github.com/samhollenbach/Galaxy2/LICENSE)
[![Release Version](https://img.shields.io/badge/release-2.1-red.svg)](https://github.com/Tencent/mars/releases)


### Galaxy2 running with the Reader.py program with 400 particles

![Example](resources/galaxy2.gif "Example Galaxy shown with the Reader.py with 400 particles")


## Background

This is a project created by Sam Hollenbach as an independent research project at Macalester College.

The simulation began as a open ended project for my Modern Astronomy course as a freshman. The first generation (Galaxy_v1) could only be visualized in 2D and had a very rudimentary Dark Matter approximation, as well as being very inefficient in many calculations. 

Galaxy_v1 can be found at [here](https://github.com/samhollenbach/Galaxy)

## Features of Galaxy2

Galaxy2 has been drasticly improved in simulation accuracy, code effciency, and visualization.


Notable features of v2.1:

-[NFW Dark Matter Profile integration](https://en.wikipedia.org/wiki/Navarro%E2%80%93Frenk%E2%80%93White_profile)

-Dark Matter analysis mode, to quickly determine how accurate the NFW profile is with specified constants

-[3D visualization](https://github.com/samhollenbach/Galaxy2/blob/master/Reader.py) using [matplotlib](http://matplotlib.org/)

-Parallel processing ability using [joblib](https://pythonhosted.org/joblib/)

-Improved code speed and readability

## Creating your own galaxy

The format for creating a galaxy in Galaxy2 is a very simple 4 steps:

```python
#Create your galaxy with specified spiral disk size, position, and star number
#Must have an id to differentiate between other galaxies
milky_way = Galaxy(galaxy_width, galaxy_height, posX, posY, posZ, starNum, id)
```

```python
#Sets the peculiar velocity of your galaxy (for interaction between multiple galaxies)
milky_way.vel = np.array([velocityX, velocityY, velocityZ])
```

```python
#Randomly distributes the stars in your galaxy 
milky_way.setstardistribution() 
```

```python
#Add this galaxy
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

Contact me at shollenb@macalester.edu if you have any quesitons
