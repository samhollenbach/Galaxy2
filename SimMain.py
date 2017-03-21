import numpy as np
import math
import sys
import time
from joblib import Parallel, delayed
from SimComponents import Star, Galaxy, printProgress
import argparse


# Writes the data for a single star at a
def write(s):
    w = "{0},{1},{2},{3},{4}\n".format(currentIteration, s.pos[0], s.pos[1], s.pos[2], s.origin.color)
    f.write(w)


# Gets distance between pos1 ([x1,y1,z1]) and  pos2 ([x2,y2,z2])
def getdist(pos1, pos2):
    p2 = np.square(pos2 - pos1)
    return math.sqrt(np.sum(p2))

# Gets the gravity vector between two stars in (SM * PC / s^2)
def getgravityvector(s1, s2):
    d = s2.pos - s1.pos
    d2 = np.square(d)
    fg = G * s1.mass * s2.mass / np.sum(d2)  # SM * PC / s^2
    vg = d
    scalar = -fg / np.linalg.norm(vg)
    vg *= scalar
    return vg

#Returns force between Star s and the center of Galaxy o using NFW Density Profile
def getdarkmatterforce(s, g):
    # Distance between star and galaxy center
    r = getdist(g.pos, s.pos)
    # Integrated dark matter mass within radius r
    mdm = 4 * math.pi * P_crit * sig * math.pow(r_s, 3) * (math.log((r_s + r) / r_s) - (r / (r_s + r)))
    # Create gravity vector for star from dark matter mass pointing at center of galaxy
    vec = g.pos - s.pos
    fgdm = G * s.mass / math.pow(r, 2) * mdm
    scale = fgdm / np.linalg.norm(vec)
    vec *= scale
    return vec

# Calculates the position of each particle after force as been applied, and writes the data to the sim_data file
def calculatemovesfromforce(t):
    for s in stars:
        a = s.force / s.mass
        s.velocity += (a * t)
        s.pos += s.velocity * t
        write(s)

#Iterates over all stars and applies applicable forces and moves
def processStars(starsTemp):
    for i in range(0, len(starsTemp) - 1):
        s = starsTemp[i]
        force = np.array([0., 0., 0.])

        for j in range(0, len(starsTemp) - 1):
            if j == i:
                continue

            next_star = starsTemp[j]
            if getdist(s.pos, next_star.pos) > 2000 and next_star.mass != next_star.origin.smbh_mass:
                continue

            # Find gravity vector calculations between each star and sum to a net force for each star
            force += getgravityvector(s, next_star)

        if s.mass != s.origin.smbh_mass:
            for galaxy_origin in galaxies:
                force += getdarkmatterforce(s, galaxy_origin)
        s.force = force
    return starsTemp

# Initiaizes a single stationary galaxy centered at the origin
def single_galaxy():
    print("\nCreating a single Galaxy for you with {:d} stars...\n".format(int(particleNum)))
    mw = Galaxy(galaxy_width, galaxy_height, 0., 0., 0., particleNum, 1)
    mw.set_pitch_roll(math.pi / 3, math.pi / 4)
    # mw.vel = np.array([0., 0., 0.])
    mw.setstardistribution()
    galaxies.append(mw)

# Initializes two galaxies heading towards each other
def double_galaxy():
    print("\nCreating two Galaxies for you, each with {:d} stars...\n".format(int(particleNum / 2)))
    mw = Galaxy(galaxy_width, galaxy_height, -20000., -15000., 0., particleNum / 2, 1)
    an = Galaxy(galaxy_width, galaxy_height, 20000., 15000., 0., particleNum / 2, 2)
    mw.set_pitch_roll(math.pi / 3, math.pi / 4)
    mw.vel = np.array([3e-11, 1e-11, 0])
    an.vel = np.array([-3e-11, -3e-11, 0])
    mw.setstardistribution()
    an.setstardistribution()
    galaxies.append(mw)
    galaxies.append(an)

# Simulation Variables and Constants #
#### ALL DISTANCE UNITS ARE IN PARSECS ####
#### ALL MASS UNITS ARE IN SOLAR MASSES ####

# Sim Vairables
iterations = 100
particleNum = 100
timeStep = 0.4e14  # Seconds (maybe should change to years)
sim_data_file = "sim_data.txt"

# Galaxy Variables
galaxy_width = 35000.
galaxy_height = 300.
G = 4.51722e-30  # G constant converted to units: PC^3 / (SM * s^2)

# NFW (Dark matter approximation) Variables
r_s = 3.1e3
c = 55  ### MILKY WAY ~10-15 ###

# NFW Constants
r_200 = c * r_s
P_crit = 3 * math.pow((67.6 / 3.09e19), 2) / (8 * math.pi * G)  # 3H^2/(8*Pi*G) --> SM/PC^3
sig = (200 / 3) * math.pow(c, 3) / (math.log(c) - (c / (1 + c)))

# 0 - Simulation, 1 - DM Analysis, 2 - Analysis and Simulation
mode = 0

# Pass in arguments for iterations/particles
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--particles", help="Number of particles to run in the simulation", type=int)
parser.add_argument("-i", "--iterations", help="Number frames the simulation will run for", type=int)
parser.add_argument("-m", "--mode", help="Modes: 0 = Simulation, 1 = Dark Matter Analysis, 2 = Both", type=int)
args = parser.parse_args()
if args.particles:
    particleNum = args.particles
if args.iterations:
    iterations = args.iterations
if args.mode:
    mode = args.mode

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
            return s.mass * np.square(s.origin.main_velo) / s.pos[0]

        def get_error(exf, dmf):
            return -(exf - dmf) / exf

        errors = []
        test_smbh = Star(test_galaxy.smbh_mass, 0, 0, 0, test_galaxy)

        # Print expected vs. actual dark matter approximations
        for s in test_galaxy.galaxy_stars:
            print("Star at radius %s" % s.pos[0])
            exf = math.fabs(expected_force(s))
            dmf = math.fabs(getdarkmatterforce(s, test_galaxy)[0] + getgravityvector(s, test_smbh)[0])
            print("Expected: %s" % exf)
            print("Actual: %s" % dmf)
            err = get_error(exf, dmf)
            errors.append(err)
            print("Error: %s" % err)
            print("\n")

        #Prints all errors
        print("All error values:")
        print(errors)
        print("\n")

    if mode == 0 or mode == 2:
        #stars = np.array
        galaxies = []

        ##########################################
        # Define either one galaxy or two galaxies
        single_galaxy()
        ##########################################

        # Calculate the timestep in year for display on sim reader
        timeStepYrs = timeStep / (60 * 60 * 24 * 365.25)
        stars = np.array([temp_star for g in galaxies for temp_star in g.galaxy_stars])

        # Opens new data file and writes header (containing number of particles)
        print("Opening sim_data file...\n")
        f = open(sim_data_file, 'w')
        f.write("HEAD:{},{}\n".format(len(galaxies), particleNum))

        #Starts counter
        simStartTime = time.perf_counter()
        updateTime = simStartTime
        currentIteration = 0

        #How many cores to run the simulation on (must be a factor of the particle number)
        n_jobs = 4

        # Start sim loop
        with Parallel(n_jobs=n_jobs) as parallelizer:
            for n in range(1, iterations + 1):

                # this iterator returns the functions to execute for each task
                tasks_iterator = (delayed(processStars)(starsTemp)
                                  for starsTemp in np.split(stars, n_jobs))
                result = parallelizer(tasks_iterator)

                #Need to update the galaxy origin once for each job array split (no idea why)
                for star_list in result:
                    star_list[0].origin.update(timeStep)

                #Combine paralleled results back into master star list
                stars = np.concatenate(result)

                # Calculate all particle moves and write them
                calculatemovesfromforce(timeStep)

                # Count iterations and print progress bar
                currentIteration += 1

                #Calculation time for this iteration
                updateTime = time.perf_counter() - simStartTime

                #Create remaining time estimate from this iteration time
                time_est = (iterations - currentIteration) * updateTime / currentIteration
                printProgress(n, iterations, prefix="Particle Position Calculation Progress:",
                              suffix="Completed. ({:d}/{:d} iterations completed, Approx. {} seconds remaining)".format(
                                  currentIteration, iterations, repr(int(time_est))) if currentIteration != iterations
                              else "Completed. ({:d}/{:d} iterations completed)".format(currentIteration, iterations),
                              barLength=50)

        # Finish
        f.close()
        simEndTime = time.perf_counter()
        totalTime = simEndTime - simStartTime
        print(
            "\nSimulation calculations completed in %s seconds! Run the sim_data.txt file in the SimReader to see your results.\n"
            % round(totalTime, 2))
