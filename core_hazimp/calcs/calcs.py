
import sys  
import inspect

class Calculator(object):

    def getargspec_call(self):
        # Returns a named tuple.
        getargspec_call = inspect.getargspec(self.__call__)
        getargspec_call.args.remove('self')
        self.allargspec_call = getargspec_call
        self.args_in = self.allargspec_call.args


class Add_a_b_test(Calculator):
    
    def __init__(self):
        self.getargspec_call()
        self.args_out = ('c')
    
    def __call__(self, a, b):
        return a + b
    

class Mult_a_c_test(Calculator):
    
    def __init__(self):
        self.getargspec_call()
        self.args_out = ('d')
    
    def __call__(self, a, c):
        return a * c
 

class Multiple_values_test(Calculator):
    
    def __init__(self):
        self.getargspec_call()
        self.args_out = ('e', 'f')
    
    def __call__(self, a, b):
        return (a, b)
                       
            
def inundation_pre_look_up_m(max_water_depth_m, floor_height_above_ground_m):
    inundation_above_floor_m = max_water_depth_m - floor_height_above_ground_m
    return {'inundation_above_floor_m':inundation_above_floor_m}
    
def add_a_b_test(a, b):
    return {'c': a + b}
    
def instanciate_classes():
    callable_instances = {}
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            instance = obj()
            if callable(instance):
                callable_instances[name] = instance
    return callable_instances

            
calulations = instanciate_classes()

