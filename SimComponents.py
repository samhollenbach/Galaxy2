import numpy as np
import math
import sys
import random


# Star position in parsecs
class Star:
    velocity = np.array([0., 0., 0.])
    force = np.array([0., 0., 0.])

    def __init__(self, mass, x, y, z, origin):
        self.mass = mass
        self.x = x
        self.y = y
        self.z = z
        self.origin = origin


class Galaxy:
    smbh_mass = 4.2e6  ###Roughly Sagittarius A* mass in solar masses###
    galaxy_bulge_width = 1000
    galaxy_bulge_height = 1000
    vel = np.array([0., 0., 0.])
    main_velo = 7.129e-12
    galaxy_stars = []

    def __init__(self, width, height, x, y, z, numstars, color):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.z = z
        self.numstars = numstars
        self.color = color
        self.setrandommultiplier()

    def setstardistribution(self):
        smbh = Star(self.smbh_mass, 0., 0., 0., self)
        self.galaxy_stars.append(smbh)
        for i in range(1, self.numstars):
            printProgress(i + 1, self.numstars, prefix="Setting Star Distributions:",
                          suffix="Completed ({}/{} stars distributed)".format(i + 1, self.numstars), barLength=50)

            # Determines random x and y position for star
            dist = self.getstarranddistributionrandomnum()
            angle = random.random() * 2 * math.pi
            x1 = dist * math.cos(angle)
            y1 = dist * math.sin(angle)

            # Determines z position for star
            if dist < self.galaxy_bulge_width:
                z1 = (self.galaxy_bulge_height * random.random()) - (self.galaxy_bulge_height / 2)
            else:
                z1 = (self.height * random.random()) - (self.height / 2)

            # Mass in solar masses
            mass = 1 * (0.8 + random.random() * 10)
            ts = Star(mass, x1, y1, z1, self)
            self.set_star_velocity(ts)
            self.galaxy_stars.append(ts)

        print("\n")
        # May need to add in color code things

    # Get the initial random multiplier to use for star distribution
    def setrandommultiplier(self):
        self.randommultiplier = 0.0
        for i in range(1, self.width):
            self.randommultiplier += self.starden(i)

    # For star distribution calculations
    def getstarranddistributionrandomnum(self):
        n = 1
        r = random.random() * self.randommultiplier
        r -= self.starden(n)

        while r >= 0:
            n += 1
            r -= self.starden(n)

        return n

    # Used to determine density of stars in galaxy by radius
    @staticmethod
    def starden(r):
        return np.exp(-r / 3000)

    # Sets star velocity perpendicular to the center of the galaxy
    def set_star_velocity(self, star):
        xt = self.x - star.x
        yt = self.y - star.y

        a = np.array([xt, yt, 0])
        r = np.linalg.norm(a)

        # Initial velocity in pc/s
        # velo = 7.129e-12  #220 km/s in pc/s
        velo = self.main_velo

        # Center of galaxy
        r1 = 1000
        if r < r1:
            velo *= (0.5 + (0.5 * r) / r1)

        # Set direction of velocity
        theta = math.atan(yt / xt)
        if xt < 0:
            velo *= -1
        vx = -velo * math.sin(theta)
        vy = velo * math.cos(theta)

        v = np.array([vx, vy, 0])
        v += self.vel
        star.velocity = v

    # Updates the position of the galactic center
    def update(self, t):
        self.x = self.vel[0] * t
        self.y = self.vel[1] * t
        self.z = self.vel[2] * t


def printProgress(iteration, total, prefix='', suffix='', decimals=1, barLength=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr = "{0:." + str(decimals) + "f}"
    percents = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '=' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, 100, '%', suffix)),
        sys.stdout.write('\n')
    sys.stdout.flush()
