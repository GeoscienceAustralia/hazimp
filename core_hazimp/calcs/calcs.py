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
        self.call_funct = None
        
        self.getargspec_call()
  
        
    def getargspec_call(self):
        """
        Automatically determine the arguments of 
        the __call__ function.
        """
        # Returns a named tuple.
        getargspec_call = inspect.getargspec(self.calc)
        getargspec_call.args.remove('self')
        self.allargspec_call = getargspec_call
        print "self.allargspec_call", self.allargspec_call
        self.args_in = self.allargspec_call.args
        self.args_out = None

                
    def calc(self):
        pass
        
    def get_call_funct(self):
        return self.call_funct
  
        
    def __call__(self, context, **kwargs):
        args_in = []
        print "self.args_in", self.args_in
        for job_arg in self.args_in:
            # A calc with no input is ok.
            if not context.exposure_att.has_key(job_arg):
                    #FIXME add warning
                print "job_arg", job_arg
                print "NO CORRECT VARIABLES" 
                import sys 
                sys.exit() 
            args_in.append(context.exposure_att[job_arg])
        args_out = self.calc(*args_in, **kwargs)
        assert len(args_out) == len(self.args_out)
        for i, arg_out in enumerate(self.args_out):
            context.exposure_att[arg_out] = args_out[i]


class AddTest(Calculator):
    """
    Simple test class, adding args together.
    """
    def __init__(self):
        super(AddTest, self).__init__()
        self.args_out = ['c_test']
        self.call_funct = 'add_test'
    
    def calc(self, a_test, b_test):
        """
        Add args
        """
        return [a_test + b_test]
    

class MultiplyTest(Calculator):
    """
    Simple test class, multiplying args.
    """
    
    def __init__(self):
        super(MultiplyTest, self).__init__()
        self.args_out = ['d_test']
        self.call_funct = 'multiply_test'
    
    def calc(self, a_test, c_test):
        """
        Multiply args
        """
        return [a_test * c_test]
 

class MultipleValuesTest(Calculator):
    """
    Simple test class, returning two values.
    """
    
    def __init__(self):
        super(MultipleValuesTest, self).__init__()
        self.args_out = ['e_test', 'f_test']
        self.call_funct = 'multiple_values_test'
    
    def calc(self, a_test, b_test):
        """
        Return two values
        """
        return [a_test, b_test]
                       

class ConstantTest(Calculator):
    """
    Simple test class, returning two values.
    """
    
    def __init__(self):
        super(ConstantTest, self).__init__()
        self.args_out = ['g_test']
        self.call_funct = 'constant_test'
    
    def calc(self, constant=None):
        """
        Return two values
        """
        return [constant*2]
                                   
#def inundation_pre_look_up_m(max_water_depth_m, floor_height_above_ground_m):
#    inundation_above_floor_m = max_water_depth_m - floor_height_above_ground_m
#    return {'inundation_above_floor_m':inundation_above_floor_m}
    
    
def instanciate_classes():
    """
    Create a dictionary of calculation names (key) and the calc instance (value)
    """
    callable_instances = {}
    for _, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            instance = obj()
            if callable(instance):
                callable_instances[instance.call_funct] = instance
    return callable_instances

            
CALCS = instanciate_classes()

