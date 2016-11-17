import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import timeit


def randrange(n, vmin, vmax):
    return (vmax - vmin)*np.random.rand(n) + vmin

fig = plt.figure()
#plt.ion()
#ax = fig.add_subplot(111, projection='3d')
ax = fig.add_subplot(111, projection='3d')
ax.has_been_closed = False
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
    plt.xlim([-80000,80000])
    plt.ylim([-40000,40000])
    #plt.zlim([-100,100])
    ax.scatter(xs, ys, c='r', marker='o')
    plt.pause(0.001)




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

        i = data[0][5:]
        if i != iter:
            iter = i
            updateplot(iter,xs,ys,zs)
            xs = []
            ys = []
            zs = []

        x = float(data[1][2:])
        y = float(data[2][2:])
        z = float(data[3][2:])
        xs.append(x)
        ys.append(y)
        zs.append(z)

plt.close()