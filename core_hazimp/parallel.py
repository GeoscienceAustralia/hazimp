# -*- coding: utf-8 -*-


"""
Functions that haven't found a proper module.
"""
import socket
import numpy


class Parallel(object):
    """ Parallelise to run on a cluster.

    Attributes:
    :param rank: What is the id of this node in the cluster.
    :param size: How many processors are there in the cluster.
    :param node: name of the cluster node.
    :param is_parallel: True if parallel is operational
    :param file_tag: A string that can be added to files to identify who
    wrote the file.
    """
    def __init__(self):
        """
        Use is_parallel = False to stop parallelism, eg when running
        several scenarios.
        """

        try:
            import pypar
        except ImportError:
            self._not_parallel()
        else:
            if pypar.size() >= 2:
                self.rank = pypar.rank()
                self.size = pypar.size()
                self.node = pypar.get_processor_name()
                self.is_parallel = True
                self.file_tag = str(self.rank)
                self.log_file_tag = str(self.rank)

                # Ensure a clean MPI exit
                import atexit
                atexit.register(pypar.finalize)
            else:
                self._not_parallel()

    def _not_parallel(self):
        """
        Set the attributes if there is only one node.
        """
        self.rank = 0
        self.size = 1
        self.node = socket.gethostname()  # The host name
        self.is_parallel = False
        self.log_file_tag = str(self.rank)


STATE = Parallel()


def spread_dict(whole):
    """
    Broadcast and recieve a dictionary where the values are 1d arrays
    and the arrays are subsetted for the workers.

    :param whole: The dictionary of 1d arrays to subset.
    :returns: (indexes of whole array, subsetted dictionary of 1d arrays)
    """
    array_len = len(whole[whole.keys()[0]])
    if not STATE.is_parallel:
        return (numpy.array(range(0, array_len)), whole)
    else:
        import pypar

    #  subsetting
    if STATE.rank == 0:
        chunks = []
        for pro in range(0, STATE.size):
            temp_indexes = numpy.array(range(pro, array_len, STATE.size))
            chunks.append(temp_indexes)
            #print "indexes",indexes
            if pro is 0:
                indexes = temp_indexes
            else:
                pypar.send(temp_indexes, pro)
            temp_subset = {}
            for key in whole.keys():
                temp_subset[key] = whole[key][temp_indexes]
            if pro is 0:
                subset = temp_subset
            else:
                pypar.send(temp_subset, pro)
    else:
        indexes = pypar.receive(0)
        subset = pypar.receive(0)
    return (indexes, subset)

#-------------------------------------------------------------
if __name__ == "__main__":
    pass
