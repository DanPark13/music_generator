## PURPOSE: Change the input data to output data
## FOR USE: generation.py

# Import necessary libraries
import theano
import theano.tensor as T
import numpy as np
import piece_parser

## Class function to be called in generation.py
class ChangeOutput(theano.Op):
    
    def make_node(self, state, time):
        state = T.as_tensor_variable(state)
        time = T.as_tensor_variable(time)
        
        return theano.Apply(self, [state, time], [T.bmatrix()])

    def perform(self, node, inputs_storage, output_storage):
        state, time = inputs_storage
        output_storage[0][0] = np.array(data_parser.get_single_input_form(state, time), dtype='int8')

    def R_op(self, inputs, eval_points):
        pass
