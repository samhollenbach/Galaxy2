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
        self.pos = np.array([x, y, z])
        self.origin = origin


class Galaxy:
    smbh_mass = 4.2e6  ###Roughly Sagittarius A* mass in solar masses###
    galaxy_bulge_width = 1000
    galaxy_bulge_height = 1000
    main_disk_vel = 7.129e-12

    def __init__(self, width, height, x, y, z, numstars, color):
        self.vel = np.array([0., 0., 0.])
        self.galaxy_stars = []
        self.width = width
        self.height = height
        self.pos = np.array([x, y, z])
        self.pitch = 0
        self.roll = 0
        self.numstars = numstars
        self.color = color
        self.set_rand_multiplier()

    def set_pitch_roll(self, pitch, roll):
        self.pitch = pitch
        self.roll = roll

    # Updates the position of the galactic center
    def update(self, t):
        self.pos = self.pos + (self.vel * t)

    def setstardistribution(self):
        smbh = Star(self.smbh_mass, self.pos[0], self.pos[1], self.pos[2], self)
        smbh.velocity = self.vel[:]
        self.galaxy_stars.append(smbh)
        for i in range(1, int(self.numstars)):
            printProgress(i + 1, self.numstars, prefix="Setting Star Distributions:",
                          suffix="Completed ({}/{} stars distributed in galaxy {})".format((i + 1), int(self.numstars),
                                                                                           self.color), barLength=50)

            # Determines random x and y position for star
            dist = self.get_star_rand_num()
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

            star_pos = np.array([self.pos[0] + x1, self.pos[1] + y1, self.pos[2] + z1])
            star_pos = self.apply_pitch_roll(star_pos)

            ts = Star(mass, star_pos[0], star_pos[1], star_pos[2], self)
            self.set_star_velocity(ts)
            self.galaxy_stars.append(ts)

        print("\n")
        # May need to add in color code things

    # Sets star velocity perpendicular to the center of the galaxy
    def set_star_velocity(self, star):
        xt = self.pos[0] - star.pos[0]
        yt = self.pos[1] - star.pos[1]

        a = np.array([xt, yt, 0])
        r = np.linalg.norm(a)

        # Initial velocity in pc/s
        # velo = 7.129e-12  #220 km/s in pc/s
        velo = self.main_disk_vel

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
        vz = 0
        v = self.apply_pitch_roll(np.array([vx, vy, vz]))
        star.velocity = v + self.vel

    # Used to determine density of stars in galaxy by radius
    @staticmethod
    def star_density(r):
        return np.exp(-r / 3000)

    # Get the initial random multiplier to use for star distribution
    def set_rand_multiplier(self):
        self.randommultiplier = 0.0
        for i in range(1, int(self.width)):
            self.randommultiplier += self.star_density(i)

    # For star distribution calculations
    def get_star_rand_num(self):
        n = 1
        r = random.random() * self.randommultiplier
        r -= self.star_density(n)
        while r >= 0:
            n += 1
            r -= self.star_density(n)
        return n

    def yaw_rot(self, alpha):
        return np.array([[math.cos(alpha), -math.sin(alpha), 0],
                         [math.sin(alpha), math.cos(alpha), 0],
                         [0, 0, 1]])

    def pitch_rot(self, beta):
        return np.array([[math.cos(beta), 0, math.sin(beta)],
                         [0, 1, 0],
                         [-math.sin(beta), 0, math.cos(beta)]])

    def roll_rot(self, gamma):
        return np.array([[1, 0, 0],
                         [0, math.cos(gamma), -math.sin(gamma)],
                         [0, math.sin(gamma), math.cos(gamma)]])

    def apply_pitch_roll(self, array):
        return array.dot(self.pitch_rot(self.pitch)).dot(self.roll_rot(self.roll))


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
