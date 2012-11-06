# -*- coding: utf-8 -*-

# pylint: disable=W0221
# Since the arguemts for __call__ will change from class to calss

"""
Need to work out the licence
"""

import sys  
import inspect

class Calculator(object):
    """
    Abstract class that automatically determines the arguments of 
    the __call__ function.
    """
    def __init__(self):
        """
        Initalise a Calculator object having the attributes
        allargspec_call and args_in.
        """
        self.allargspec_call = None
        self.args_in = None
        #self.call_funct = None
        
        self.getargspec_call()
        
    def getargspec_call(self):
        """
        Automatically determine the arguments of 
        the __call__ function.
        """
        # Returns a named tuple.
        getargspec_call = inspect.getargspec(self.__call__)
        getargspec_call.args.remove('self')
        self.allargspec_call = getargspec_call
        self.args_in = self.allargspec_call.args
        
    def __call__(self, *args):
        pass


class AddTest(Calculator):
    """
    Simple test class, adding args together.
    """
    def __init__(self):
        super(AddTest, self).__init__()
        self.args_out = ('c_test')
    
    def __call__(self, a_test, b_test):
        """
        Add args
        """
        return a_test + b_test
    

class MultiplyTest(Calculator):
    """
    Simple test class, multiplying args.
    """
    
    def __init__(self):
        super(MultiplyTest, self).__init__()
        self.args_out = ('d_test')
    
    def __call__(self, a_test, c_test):
        """
        Multiply args
        """
        return a_test * c_test
 

class MultipleValuesTest(Calculator):
    """
    Simple test class, returning two values.
    """
    
    def __init__(self):
        super(MultipleValuesTest, self).__init__()
        self.args_out = ('e_test', 'f_test')
    
    def __call__(self, a_test, b_test):
        """
        Return two values
        """
        return (a_test, b_test)
                       
            
#def inundation_pre_look_up_m(max_water_depth_m, floor_height_above_ground_m):
#    inundation_above_floor_m = max_water_depth_m - floor_height_above_ground_m
#    return {'inundation_above_floor_m':inundation_above_floor_m}
    
    
def instanciate_classes():
    """
    Create a dictionary of calculation names (key) and the calc instance (value)
    """
    callable_instances = {}
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            instance = obj()
            if callable(instance):
                callable_instances[name] = instance
    return callable_instances

            
CALCS = instanciate_classes()

