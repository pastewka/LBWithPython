'''
Remider CodingRules:
Zeilenumbruch bei Spalte 120
Modulname, Klassennamen als CamelCase
Variablennamen, Methodennamen, Funktionsnamen mit unter_strichen
Bitte nicht CamelCase und Unterstriche mischen
'''

'''
I have made the decission to not include anything form the tests 
or from the original code itself.
This module should be able to work on its own, but it will be with basically no explanation in the code itself
for this look at the simpleFlowsTest.
'''

# Todo: remove me
'''
my todos:
implement the sliding lid 3 boundaries just as bounce back, 1 is sliding over it
needs streaming, collision, equilibrium, bounce back but more complicated
use streamplot for a visualization
could rework the bounce back to be more streamlined
'''
# imports
import numpy as np
import matplotlib.pyplot as plt

# initial variables and sizes
size_x = 50
size_y = 50
relaxation = 0.5
velocity_set = np.array([[0, 1, 0, -1, 0, 1, -1, -1, 1],
                         [0,0,1,0,-1,1,1,-1,-1]]).T
# main methods
def stream(grid):
    for i in range(1,9):
        grid[i] = np.roll(grid[i],velocity_set[i], axis = (0,1))

def equilibrium(rho,ux,uy):
    uxy_3plus = 3 * (ux + uy)
    uxy_3miuns = 3 * (ux - uy)
    uu = 3 * (ux * ux + uy * uy)
    ux_6 = 6 * ux
    uy_6 = 6 * uy
    uxx_9 = 9 * ux * ux
    uyy_9 = 9 * uy * uy
    uxy_9 = 9 * ux * uy
    return np.array([(2 * rho / 9) * (2 - uu),
                     (rho / 18) * (2 + ux_6 + uxx_9 - uu),
                     (rho / 18) * (2 + uy_6 + uyy_9 - uu),
                     (rho / 18) * (2 - ux_6 + uxx_9 - uu),
                     (rho / 18) * (2 - uy_6 + uyy_9 - uu),
                     (rho / 36) * (1 + uxy_3plus + uxy_9 + uu),
                     (rho / 36) * (1 - uxy_3miuns - uxy_9 + uu),
                     (rho / 36) * (1 - uxy_3plus + uxy_9 + uu),
                     (rho / 36) * (1 + uxy_3miuns - uxy_9 + uu)])

def collision(grid,rho,ux,uy):
    grid -= relaxation * (grid - equilibrium(rho, ux, uy))

def caluculate_rho_ux_uy(grid):
    rho = np.sum(grid, axis=0)  # sums over each one individually
    ux = ((grid[1] + grid[5] + grid[8]) - (grid[3] + grid[6] + grid[7])) / rho
    uy = ((grid[2] + grid[5] + grid[6]) - (grid[4] + grid[7] + grid[8])) / rho
    return rho,ux,uy

def bounce_back(grid,uw):
    #### Left + Right
    # right so x = 0
    grid[1, 1, :] = grid[3, 0, :]
    grid[5, 1, :] = np.roll(grid[7, 0, :],1)
    grid[8, 1, :] = np.roll(grid[6, 0, :],-1)
    # left so x = -1
    grid[3, -2, :] = grid[1, -1, :]
    grid[6, -2, :] = np.roll(grid[8, -1, :],1)
    grid[7, -2, :] = np.roll(grid[5, -1, :],-1)
    ### TOP + Bottom
    # for bottom y = 0
    grid[2, :, 1] = grid[4, :, 0]
    grid[5, :, 1] = np.roll(grid[7, :, 0], 1)
    grid[6, :, 1] = np.roll(grid[8, :, 0], -1)
    # for top y = -1
    grid[4, :, -2] = grid[2, :, -1]
    grid[7, :, -2] = np.roll(grid[5, :, -1], 1) - 1 / 6 * uw
    grid[8, :, -2] = np.roll(grid[6, :, -1], -1) + 1 / 6 * uw

# body
def sliding_lid():
    print("Sliding Lid")
    # init the variables
    steps = 10000
    uw = 0.01

    # initizlize the gird
    rho = np.ones((size_x+2,size_y+2))
    ux = np.zeros((size_x+2,size_y+2))
    uy = np.zeros((size_x+2,size_y+2))
    grid = equilibrium(rho,ux,uy)

    # loop
    for i in range(steps):
        stream(grid)
        bounce_back(grid,uw)
        rho, ux, uy = caluculate_rho_ux_uy(grid)
        collision(grid,rho,ux,uy)

    # visualize
    x = np.arange(0, size_x)
    y = np.arange(0, size_y)
    X, Y = np.meshgrid(x, y)
    plt.streamplot(X,Y,ux[1:-1,1:-1],uy[1:-1,1:-1])
    plt.show()



# call
sliding_lid()