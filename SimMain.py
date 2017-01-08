import numpy as np
import math
import random
import sys
import time
from joblib import Parallel, delayed
from SimComponents import Star
from SimComponents import Galaxy


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




# Initiaizes a single stationary galaxy centered at the origin
def single_galaxy():
    print("Creating a single Galaxy for you with %s stars...\n" % particleNum)
    mw = Galaxy(galaxy_width, galaxy_height, 0, 0, 0, particleNum, 1)
    mw.velocity = np.array([0, 0, 0])
    mw.setstardistribution()
    galaxies.append(mw)


# Initializes two galaxies heading towards each other
def double_galaxy():
    print("Creating two Galaxies for you with %s stars each...\n" % (particleNum / 2))
    mw = Galaxy(galaxy_width, galaxy_height, -80000, -60000, 0, particleNum / 2, 1)
    an = Galaxy(galaxy_width, galaxy_height, 80000, 60000, 0, particleNum / 2, 2)
    mw.velocity = np.array([10, 1, 0])
    an.velocity = np.array([-10, -1, 0])
    mw.setstardistribution()
    an.setstardistribution()
    galaxies.append(mw)
    galaxies.append(an)


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
    return vg


#Returns force between Star s and the center of Galaxy o using NFW Density Profile
def getdarkmatterforce(s, g):

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

def processStars(starsTemp):
    for i in range(0, len(starsTemp) - 1):
        s = starsTemp[i]
        force = np.array([0., 0., 0.])

        for j in range(0, len(starsTemp) - 1):
            if j == i:
                continue

            # Find gravity vector calculations between each star and sum to a net force for each star'

            # CHECK DISTANCE BETWEEN S and STARS[j] : IF GREATER THAN CERTAIN THRESHOLD THEN SKIP THIS CALCULATION TO IMPROVE PERFORMANCE
            g = getgravityvector(s, starsTemp[j])
            force += g

        if s.mass != s.origin.smbh_mass:
            dm = getdarkmatterforce(s, s.origin)
            force += dm
        s.force = force
    return starsTemp

# Calculates the position of each particle after force as been applied, and writes the data to the sim_data file
def calculatemovesfromforce(t):
    for s in stars:
        a = s.force / s.mass
        s.velocity += (a * t)
        s.x += s.velocity[0] * t
        s.y += s.velocity[1] * t
        s.z += s.velocity[2] * t
        write(s)

# RUN_READER = True
# RECALC_DIST = True

# Simulation Variables and Constants #
#### ALL DISTANCE UNITS ARE IN PARSECS ####
#### ALL MASS UNITS ARE IN SOLAR MASSES ####

# Sim Vairables
iterations = 200
particleNum = 100
timeStep = 0.4e14  # Seconds
# galaxy_data_file = "galaxy_data.txt"
sim_data_file = "sim_data.txt"

# Galaxy Variables

galaxy_width = 35000
galaxy_height = 300
stars = []
galaxies = []
G = 4.51722e-30  # G constant converted to units: PC^3 / (SM * s^2)

# NFW Variablesy
r_s = 0.031e5
r_200 = 55 * r_s  # Higher pulls outside stronger, inside weaker
c = r_200 / r_s  ## MILKY WAY ~10-15 --> Set to 12.5

# NFW Constants
P_crit = 3 * math.pow((67.6 / 3.09e19), 2) / (8 * math.pi * G)  # 3H^2/(8*Pi*G) --> SM/PC^3
sig = (200 / 3) * math.pow(c, 3) / (math.log(c) - (c / (1 + c)))

# 0 - Simulation, 1 - DM Analysis, 2 - Analysis and Simulation
mode = 0

#######START SIMULATION RUN#########
if __name__ == '__main__':

    if mode == 1 or mode == 2:
        print("Running Dark Matter Analysis with r_scale value of %s and concentration value of %s \n" % (r_s, c))
        test_star_num = 10
        test_galaxy = Galaxy(galaxy_width, galaxy_height, 0, 0, 0, test_star_num, 0)

        # Created test_star_num stars at even intervals out from center of galaxy on x axis
        for i in range(1, (test_star_num)):
            test_x = (i / test_star_num) * galaxy_width / 2
            test_galaxy.galaxy_stars.append(Star(1, test_x, 0, 0, test_galaxy))


        #Calculates expected force for an orbit with main_velo
        def expected_force(s):
            return s.mass * np.square(s.origin.main_velo) / s.x


        def get_error(exf, dmf):
            return -(exf - dmf) / exf


        errors = []
        test_smbh = Star(test_galaxy.smbh_mass, 0, 0, 0, test_galaxy)

        for s in test_galaxy.galaxy_stars:
            print("Star at radius %s" % s.x)
            exf = math.fabs(expected_force(s))
            dmf = math.fabs(getdarkmatterforce(s, test_galaxy)[0] + getgravityvector(s, test_smbh)[0])
            print("Expected: %s" % exf)
            print("Actual: %s" % dmf)
            err = get_error(exf, dmf)
            errors.append(err)
            print("Error: %s" % err)
            print("\n")

        print("All error values:")
        print(errors)
        print("\n")

    if mode == 0 or mode == 2:

        ##########################################
        # Define either one galaxy or two galaxies
        single_galaxy()
        ##########################################

        # Calculate the timestep in year for display on sim reader
        timeStepYrs = timeStep / (60 * 60 * 24 * 365.25)
        stars = [temp_star for g in galaxies for temp_star in g.galaxy_stars]

        # Opens new data file and writes header (containing number of particles)
        print("Opening sim_data file...\n")
        f = open(sim_data_file, 'w')
        f.write("HEAD:particles=" + repr(particleNum) + "\n")

        simStartTime = time.perf_counter()
        updateTime = simStartTime
        currentIteration = 0

        n_jobs = 4

        # Start sim loop
        with Parallel(n_jobs=n_jobs) as parallelizer:
            for n in range(1, iterations + 1):

                # Update galactic center positions
                for g in galaxies:
                    g.update(timeStep)

                stars1 = np.array(stars)
                # this iterator returns the functions to execute for each task
                tasks_iterator = (delayed(processStars)(starsTemp)
                                  for starsTemp in np.split(stars1, n_jobs))
                result = parallelizer(tasks_iterator)
                stars = np.concatenate(result)

                # Calculate all particle moves and write them
                calculatemovesfromforce(timeStep)

                # Count iterations and print progress bar
                currentIteration += 1
                updateTime = time.perf_counter() - simStartTime
                time_est = (iterations - currentIteration) * updateTime / currentIteration
                printProgress(n, iterations, prefix="Particle Position Calculation Progress:",
                              suffix="Completed. (%s/%s iterations completed, Approx. %s seconds remaining)" % (
                              currentIteration, iterations, repr(int(time_est))),
                              barLength=50)

        # Finished
        f.close()
        simEndTime = time.perf_counter()
        totalTime = simEndTime - simStartTime
        print(
            "\n\nSimulation calculations completed in %s seconds! Run the sim_data.txt file in the SimReader to see your results.\n" % round(
                totalTime, 2))
