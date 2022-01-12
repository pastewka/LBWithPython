
# Todo: remove us
'''
To get a basic feel for LB-Sim implement the  Poiseuille Flow between two plates


'''
'''
Remider CodingRules: 
Zeilenumbruch bei Spalte 120
Modulname, Klassennamen als CamelCase
Variablennamen, Methodennamen, Funktionsnamen mit unter_strichen
Bitte nicht CamelCase und Unterstriche mischen
'''
# imports
import numpy as np
import matplotlib.pyplot as plt

# global variables
relaxation = 0.5
size_x = 50
size_y = 50
velocity_set = np.array([[0, 1, 0, -1, 0, 1, -1, -1, 1],
                         [0,0,1,0,-1,1,1,-1,-1]]).T

def equilibrium_on_array(rho,ux,uy):
    '''
    Calculates the equilibrium function for the whole array at once
    Parameters
    ----------
    rho
    ux
    uy

    Returns
    -------

    '''
    uxy = 3 * (ux + uy)
    uu =  3 * (ux * ux + uy * uy)
    ux_6 = 6*ux
    uy_6 = 6*uy
    uxx_9 = 9 * ux*ux
    uyy_9 = 9 * uy*uy
    uxy_9 = 9 * ux*uy
    return np.array([(2 * rho / 9) * (2 - uu),
                     (rho / 18) * (2 + ux_6 + uxx_9 - uu),
                     (rho / 18) * (2 + uy_6 + uyy_9 - uu),
                     (rho / 18) * (2 - ux_6 + uxx_9 - uu),
                     (rho / 18) * (2 - uy_6 + uyy_9 - uu),
                     (rho / 36) * (1 + uxy + uxy_9 + uu),
                     (rho / 36) * (1 - uxy - uxy_9 + uu),
                     (rho / 36) * (1 - uxy + uxy_9 + uu),
                     (rho / 36) * (1 + uxy - uxy_9 + uu)])


def collision(grid,rho,ux,uy):
    '''
    Performs the collision step and also calculated rho, ux, uy in the same step
    Parameters
    ----------
    grid

    Returns
    -------
    rho, ux, uy
    '''

    # calculate equilibrium + apply collision
    # grid = grid - relaxation * (grid - equilbrium)
    grid -= relaxation * (grid-equilibrium_on_array(rho,ux,uy))

def caluculate_real_values(grid):
    '''
    Calculates rho, ux, uy
    Parameters
    ----------
    grid

    Returns
    -------

    '''
    rho = np.sum(grid, axis=0)  # sums over each one individually
    ux = ((grid[1] + grid[5] + grid[8]) - (grid[3] + grid[6] + grid[7])) / rho
    uy = ((grid[2] + grid[5] + grid[6]) - (grid[4] + grid[7] + grid[8])) / rho
    return rho,ux,uy

def stream(grid):
    '''
    Performs the streaming step in place
    Parameters
    ----------
    grid

    Returns
    -------

    '''
    for i in range(1,9):
        grid[i] = np.roll(grid[i],velocity_set[i], axis = (0,1))

def bounce_back(grid,uw):
    '''
    Perfomrs the bounce back
    Parameters
    ----------
    grid
    uw

    Returns
    -------

    '''
    # baunce back without any velocity gain
    # TODO rho Wall missing
    max_size_x = grid.shape[1]-1  # x
    max_size_y = grid.shape[2]-1  # y
    # for bottom y = 0
    grid[2, :, 1] = grid[4, :, 0]
    grid[5, :, 1] = grid[7, :, 0]
    grid[6, :, 1] = grid[8, :, 0]
    grid[4, :, 0] = 0
    grid[7, :, 0] = 0
    grid[8, :, 0] = 0
    # for top y = max_size_y
    grid[4, :, max_size_y - 1] = grid[2, :, max_size_y]
    grid[7, :, max_size_y - 1] = grid[5, :, max_size_y] - 1 / 6 * uw
    grid[8, :, max_size_y - 1] = grid[6, :, max_size_y] + 1 / 6 * uw
    grid[2, :, max_size_y] = 0
    grid[5, :, max_size_y] = 0
    grid[6, :, max_size_y] = 0

def periodic_boundary_with_pressure_variations(grid):
    rho_null = 1
    p = 1 / 3 * rho_null
    delta_p = 0.001
    # recalculated p into rho and put it in an array
    rho_in = (p + delta_p) * 3 * np.ones((grid.shape[1]))
    rho_out = (p - delta_p) * 3 * np.ones((grid.shape[1]))

    # get all the values
    rho, ux, uy = caluculate_real_values(grid)
    equilibrium = equilibrium_on_array(rho, ux, uy)

    ##########
    equilibrium_in = equilibrium_on_array(rho_in, ux[:, -1], uy[:, -1])
    # inlet 1,5,8
    grid[1, 0, :] = equilibrium_in[1] + (grid[1, -1, :] - equilibrium[1, -1, :])
    grid[5, 0, :] = equilibrium_in[5] + (grid[5, -1, :] - equilibrium[5, -1, :])
    grid[8, 0, :] = equilibrium_in[8] + (grid[8, -1, :] - equilibrium[8, -1, :])

    # outlet 3,6,7
    equilibrium_out = equilibrium_on_array(rho_out, ux[:, 0], uy[:, 0])
    # check for correct sizes
    grid[3, -1, :] = equilibrium_out[3] + (grid[3, 0, :] - equilibrium[3, 0, :])
    grid[6, -1, :] = equilibrium_out[6] + (grid[6, 0, :] - equilibrium[6, 0, :])
    grid[7, -1, :] = equilibrium_out[7] + (grid[7, 0, :] - equilibrium[7, 0, :])


#########
def couette_flow():
    # main code
    print("couette Flow")
    steps = 5000
    uw = 1

    # initialize
    rho = np.ones((size_x,size_y+2))
    ux = np.zeros((size_x, size_y + 2))
    uy = np.zeros((size_x,size_y + 2))
    grid = equilibrium_on_array(rho,ux,uy)

    # loop
    for i in range(steps):
        rho, ux, uy = caluculate_real_values(grid)
        collision(grid,rho,ux,uy)
        stream(grid)
        bounce_back(grid,uw)

    # visualize
    x = np.arange(0,size_x)
    y = np.arange(0,size_y)
    X,Y = np.meshgrid(x,y)
    #plt.streamplot(X,Y,ux[:,1:51],uy[:,1:51])
    #plt.show()
    # stolen couette flowl code ;)
    plt.plot(ux[5,1:-2])
    plt.xlabel('Position in cross section')
    plt.ylabel('velocity')
    plt.title('Couette flow')
    plt.show()


def poiseuille_flow():
    # main code
    print("Poiseuille Flow")
    steps = 1000
    uw = 0

    # initialize
    rho = np.ones((size_x+2, size_y + 2))
    ux = np.zeros((size_x+2, size_y + 2))
    uy = np.zeros((size_x+2, size_y + 2))
    grid = equilibrium_on_array(rho, ux, uy)

    # loop
    for i in range(steps):
        rho, ux, uy = caluculate_real_values(grid)
        collision(grid, rho, ux, uy)
        stream(grid)
        bounce_back(grid, uw)
        periodic_boundary_with_pressure_variations(grid)

    # visualize
    x = np.arange(0, size_x)
    y = np.arange(0, size_y)
    X, Y = np.meshgrid(x, y)
    # plt.streamplot(X,Y,ux[:,1:51],uy[:,1:51])
    # plt.show()
    # stolen couette flowl code ;)
    plt.plot(ux[5, 1:-2])
    plt.xlabel('Position in cross section')
    plt.ylabel('velocity')
    plt.title('Pouisuelle flow')
    plt.show()


####
# function
#couette_flow()
poiseuille_flow()


