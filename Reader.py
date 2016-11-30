import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import timeit

# DOES NOT CLOSE PROPERLY WHEN TRUE
REPEAT = False


def randrange(n, vmin, vmax):
    return (vmax - vmin)*np.random.rand(n) + vmin

fig = plt.figure()
#plt.ion()
#ax = fig.add_subplot(111, projection='3d')
ax = fig.add_subplot(111, projection='3d')
ax.has_been_closed = False
ax.set_axis_bgcolor('black')
n = 100
plt.xlim([-80000,80000])
plt.ylim([-40000,40000])


ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

def on_close(event):
    event.canvas.figure.axes[0].has_been_closed = True


fig.canvas.mpl_connect('close_event', on_close)

def updateplot(iteration,xs,ys,zs):
    ax.clear()
    plt.title(repr(iteration))
    plt.xlim([-80000,80000])
    plt.ylim([-40000,40000])
    # plt.zlim([-1000,1000])
    ax.scatter(xs, ys, c='y', marker='o')
    plt.pause(0.001)


def read_sim():
    with open('sim_data.txt', 'r') as f:
        iter = -1

        xs = []
        ys = []
        zs = []

        for line in f:

            if ax.has_been_closed:
                break

            if line.startswith("HEAD:"):
                particle_num = int(line[15:])
                continue

            data = line.split(',')

            i = data[0]
            if i != iter:
                iter = i
                updateplot(iter, xs, ys, zs)
                xs = []
                ys = []
                zs = []

            x = float(data[1])
            y = float(data[2])
            z = float(data[3])
            xs.append(x)
            ys.append(y)
            zs.append(z)


read_sim()
while REPEAT:
    read_sim()

plt.close()