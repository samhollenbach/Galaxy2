import numpy as np
import math
import random
import sys, idlelib.PyShell
#import Reader
idlelib.PyShell.warning_stream = sys.stderr
from datetime import datetime

# RUN_READER = True
# RECALC_DIST = True


# Simulation Variables and Constants #
#### ALL DISTANCE UNITS ARE IN PARSECS ####
#### ALL MASS UNITS ARE IN SOLAR MASSES ####

# Sim Vairables
iterations = 300
particleNum = 250
timeStep = 1e14  # Seconds
galaxy_data_file = "galaxy_data.txt"
sim_data_file = "sim_data.txt"

# Galaxy Variables
smbh_mass = 4.2e6  ###Roughly Sgittarius A* mass in solar masses###
galaxy_width = 35000
galaxy_height = 300
galaxy_bulge_width = 1000
galaxy_bulge_height = 1000
stars = []
galaxies = []
G = 4.51722e-30  # G constant converted to units: PC^3 / (SM * s^2)


# NFW Variables
r_s = 0.87e5
r_200 = 10 * r_s
c = r_200 / r_s  ## MILKY WAY ~10-15 --> Set to 12.5

# NFW Constants
P_crit = 3 * math.pow((67.6 / 3.09e19), 2) / (8 * math.pi * G)  # 3H^2/(8*Pi*G) --> SM/PC^3
sig = (200 / 3) * math.pow(c, 3) / (math.log(c) - (c / (1 + c)))


#Prints a progress bar which updates while running a computational loop
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


def getdist(x, y, z, x1, y1, z1):
    return math.sqrt(math.pow((x1 - x), 2) + math.pow((y1 - y), 2) + math.pow((z1 - z), 2))


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
    vel = np.array([0., 0., 0.])
    stars = []

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
        smbh = Star(smbh_mass, 0., 0., 0., self)
        stars.append(smbh)
        for i in range(1, self.numstars):
            printProgress(i + 1, self.numstars, prefix="Setting Star Distributions:", suffix="Completed", barLength=50)

            #Determines random x and y position for star
            dist = self.getstarranddistributionrandomnum()
            dist2 = dist * dist
            m = random.random() * 2 + 1
            y1 = math.sqrt(dist2 / (m * m))
            x1 = math.sqrt(dist2 - (y1 * y1))

            sign = [1, -1]
            x1 *= random.choice(sign)
            y1 *= random.choice(sign)

            # Determines z position for star
            if dist < galaxy_bulge_width:
                z1 = (galaxy_bulge_height * random.random()) - (galaxy_bulge_height / 2)
            else:
                z1 = (self.height * random.random()) - (self.height/2)


            # Mass in solar masses
            mass = 1 * (0.8 + random.random() * 10)
            ts = Star(mass, x1, y1, z1, self)
            self.set_star_velocity(ts)
            stars.append(ts)

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
        velo = 7.129e-12

        # Center of galaxy
        r1 = 1000
        if r < r1:
            velo *= (0.5 + (0.5 * r) / r1)

        # Set direction of velocity
        theta = math.atan(yt / xt)
        if xt < 0:
            r *= -1
        tempX = -(r * math.cos(theta - 0.00001) - r * math.cos(theta))
        tempY = -tempX * xt / yt

        v = np.array([tempX, tempY, 0])
        speedscale = (velo / np.linalg.norm(v))
        v *= speedscale
        v += self.vel
        star.velocity = v

    # Updates the position of the galactic center
    def update(self, t):
        self.x = self.vel[0] * t
        self.y = self.vel[1] * t
        self.z = self.vel[2] * t


# Initiaizes a single stationary galaxy centered at the origin
def single_galaxy():
    print("Creating a single Galaxy for you...\n")
    stars = []
    mw = Galaxy(galaxy_width, galaxy_height, 0, 0, 0, particleNum - 1, 1)
    mw.velocity = np.array([0, 0, 0])
    mw.setstardistribution()
    galaxies.append(mw)
    # stars.append(mw.stars)


# Initializes two galaxies heading towards each other
def double_galaxy():
    print("Creating two Galaxies for you...\n")
    stars = []
    mw = Galaxy(galaxy_width, galaxy_height, -80000, -60000, 0, particleNum / 2 - 1, 1)
    an = Galaxy(galaxy_width, galaxy_height, 80000, 60000, 0, particleNum / 2 - 1, 2)
    mw.velocity = np.array([10, 1, 0])
    an.velocity = np.array([-10, -1, 0])
    mw.setstardistribution()
    an.setstardistribution()
    galaxies.append(mw)
    galaxies.append(an)
    # stars.append(mw.stars)
    # stars.append(mw.stars)


##########################################
# Define either one galaxy or two galaxies
single_galaxy()
##########################################

# Calculate the timestep in year for display on sim reader
timeStepYrs = timeStep / (60 * 60 * 24 * 365.25)


# Opens new data file and writes header (containing number of particles)
print("Writing sim_data file...\n")
f = open(sim_data_file, 'w')
f.write("HEAD:particles=" + repr(particleNum) + "\n")


# Writes the data for a single star at a
def write(s):
    # w = "iter={0},X={1},Y={2},Z={3},c={4}\n".format(currentIteration, s.x, s.y, s.z, s.origin.color)
    w = "{0},{1},{2},{3},{4}\n".format(currentIteration, s.x, s.y, s.z, s.origin.color)
    f.write(w)


# Gets the gravity vector between two stars in (SM * PC / s^2)
def getgravityvector(s1, s2):
    dx = s2.x - s1.x
    dy = s2.y - s1.y
    dz = s2.z - s1.z

    fg = G * s1.mass * s2.mass / (dx * dx + dy * dy + dz * dz)  # SM * PC / s^2

    vg = np.array([dx, dy, dz])
    scalar = -fg / np.linalg.norm(vg)
    vg *= scalar
    #print(vg)
    return vg


#Returns force between Star s and the center of Galaxy o using NFW Density Profile
def getdarkmatterforce(s, g):
    # r_crit = 0

    # Distance between star and galaxy center
    r = getdist(g.x, g.y, g.z, s.x, s.y, s.z)

    # Integrated dark matter mass within radius r
    mdm = 4 * math.pi * P_crit * sig * math.pow(r_s, 3) * (math.log((r_s + r) / r_s) - (r / (r_s + r)))

    # Create gravity vector for star from dark matter mass pointing at center of galaxy
    vec = np.array([g.x, g.y, g.z]) - np.array([s.x, s.y, s.z])
    fgdm = G * s.mass / math.pow(r, 2) * mdm
    scale = fgdm / np.linalg.norm(vec)
    vec *= scale
    return vec

# Calculates the position of each particle after force as been applied, and writes the data to the sim_data file
def calculatemovesfromforce(t):
    for s in stars:
        a = s.force / s.mass
        s.velocity += (a * t)
        s.x += s.velocity[0] * t
        s.y += s.velocity[1] * t
        s.z += s.velocity[2] * t

        write(s)




#######START SIMULATION RUN#########

simStartTime = datetime.now().time()
updateTime = simStartTime
currentIteration = 0

# Start sim loop
for n in range(1, iterations+1):

    # Update galactic center positions
    for g in galaxies:
        g.update(timeStep)

    for i in range(0, len(stars) - 1):
        s = stars[i]
        force = np.array([0., 0., 0.])

        for j in range(0, len(stars) - 1):
            if j == i:
                continue

            # Find gravity vector calculations between each star and sum to a net force for each star
            g = getgravityvector(s, stars[j])
            force += g

        if s.mass != smbh_mass:
            dm = getdarkmatterforce(s, s.origin)
            force += dm
        s.force = force

    # Calculate all particle moves and write them
    calculatemovesfromforce(timeStep)

    # Count iterations and print progress bar
    currentIteration += 1
    printProgress(n, iterations, prefix="Particle Position Calculation Progress:", suffix="Completed.",
                  barLength=50)

# Finished
f.close()
print("\n\nSimulation calculations have completed! Run the sim_data.txt file in the SimReader to see your results.\n")