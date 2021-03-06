#!/usr/bin/python
#
## hmm model params for SIMPLE 4-state BT
import numpy as np
#from abt_constants import *
# from abtclass import *

#
FIRSTSYMBOL = 25
names = ['l1','l2','l3','l4', 'OutS', 'OutF']

N = len(names)

# PS = prob of success for each node
# note dummy value for PS[0] for math consistency
PS = [0, 0.5, 0.5, .5, 0.5, 1.0,1.0]
if len(PS) != N+1:
    print ('Incorrect PS length')
    quit()

# INITIAL State Transition Probabilities
#  make A one bigger to make index human
A = np.zeros((N+1,N+1))
A[1,2] = PS[1]
A[1,6] = 1.0-PS[1]
A[2,3] = PS[2]
A[2,6] = 1.0-PS[2]
A[3,4] = 1.0-PS[3]
A[3,5] = PS[3]
A[4,5] = PS[4]
A[4,6] = 1.0-PS[4]
A[5,5] = 1.0
A[6,6] = 1.0

A = A[1:N+1,1:N+1]  # get zero offset index

#  these values are place-holders, replaced later
outputs = {'l1':2, 'l2': 5, 'l3':8, 'l4': 8,  'OutS':10, 'OutF':20}

## Model class takes care of this now
#Pi = np.zeros(N)
#Pi[0] = 1.0      # always start at state 1

#  This is probably not nesc:   names.index('l3') == 2
statenos = {'l1':1, 'l2': 2, 'l3':3, 'l4':4,  'OutS':5, 'OutF':6}

di = 2  # placeholder

###  Regenerate output means:
i = FIRSTSYMBOL
#di = Ratio*sig  # = nxsigma !!  now in abt_constants
for n in outputs.keys():
    outputs[n] = i
    i += di

# modelo00 = model(len(names))  # make a new model
# modelo00.A = A
# modelo00.PS = PS
# modelo00.outputs = outputs
# modelo00.statenos = statenos
# modelo00.names = names
# modelo00.sigma = sig
