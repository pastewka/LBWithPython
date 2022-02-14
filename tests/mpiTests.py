'''
Test- and Playground for the mpi implementation
    -> i have to content with 2 cores thou should just get a general handle for the
    processes involved, as an alternative i could us my own pc as a testbed (6 cores)
    -> should get a general feel for all the precesses on here
        -> most important send recive
        -> create the cartisian thingi

'''
# TODO
'''
 -> monte carlo implementation get the first feel ;<;
 -> send and recive random stuff
    -> maybe do some unittests here not sure thou ;<;
 -> try out domain decomposition i guess (sendrecv lol)
 -> test the seperation into top left usw.
'''
import unittest
from mpi4py import MPI
import ipyparallel as ipp

# basic core count
cores = 2

def mpi_example():
    comm = MPI.COMM_WORLD
    return f"Hello World from rank {comm.Get_rank()}. total ranks={comm.Get_size()}"

# try out the monte carlo stuff
# basically stole out of the lecture and modified it a bit lol
def monte_carlo():
    import numpy as np
    ###
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    ###
    ntotal = 1000000
    nlocal = ntotal//size
    print(nlocal)
    if rank == 0:
        # for all the cases when it can not be divided equally
        nlocal = ntotal - nlocal*(size-1)
        #
    x = np.random.random(nlocal)
    y = np.random.random(nlocal)

    nsucess = (x**2 + y**2 < 1).sum()

    reduced_nsucess = np.array(0)
    comm.Reduce(nsucess,reduced_nsucess, op= MPI.SUM, root = 0)
    return f"{4*reduced_nsucess/ntotal}"

def data_exchanger():
    # for some reason i have to do this
    import numpy as np
    import time
    ###
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    ###
    time.sleep(rank) # sleps 0 or 1 s
    ###
    return_value = np.arange(0,10)
    if rank == 0:
        return_value = return_value*3
        # send the value to the next rank
        comm.Send(return_value,dest=1,tag=99)
    elif rank == 1:
        values = np.arange(0,10)
        comm.Recv(values,source=0,tag=99)
        return_value = values

    return f"{return_value}"



# Main caller
# request an MPI cluster with 2 engines
with ipp.Cluster(engines='mpi', n=cores
                 ) as rc:
    # get a broadcast_view on the cluster which is best
    # print(rc.ids)
    # suited for MPI style computation
    view = rc.broadcast_view()
    # run the mpi_example function on all engines in parallel
    r = view.apply_async(data_exchanger)
    # Retrieve and print the result from the engines
    print("\n".join(r))
# at this point, the cluster processes have been shutdow
