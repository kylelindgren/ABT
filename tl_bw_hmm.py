#!/usr/bin/python
#
#   Top-level scripted task

#  Unify the former tl_bw_hmm_{a,b,c,d} with command line arg.
#
#   21-Aug  see spreadsheet:
# https://docs.google.com/spreadsheets/d/1Ky3YH7SmxLFGL0PH2aNlbJbTtUTGU-UjAokIZUBkl9M/edit#gid=0
#

#   Baum Welch tests

import sys
import os
import subprocess
import uuid
import datetime
from hmm_bt import *
from abt_constants import *

#MODEL = SMALL 
MODEL = BIG

##
#    Supress Deprecation Warnings from hmm_lean / scikit
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

##   Set up research parameters mostly in abt_constants.py

 
############################################
#
#        Basic Job Config
#

NEWDATA = True  # flag to generate data once

task = BaumWelch   # Viterbi / Forward
 

script_name = 'bw_hmm'


# amount HMM parameters should be ofset
#   from the ABT parameters.  Offset has random sign (+/-)

if len(sys.argv) != 2:
    print 'Please use a single command line argument:'
    print ' > tl_bw_hmm    X.XXX'
    print '  to indicate the HMM perturbation value (0.0--1.0)'
    quit()
    
HMM_delta = float(sys.argv[1])

#
############################################

##  The ABT file for the task (CHOOSE ONE)

if MODEL== BIG:
    from peg2_ABT import * # big  14+2 state  # uses model01.py
if MODEL==SMALL:
    from simp_ABT import *  # small 4+2 state # uses model02.py

#############################################
#
#      Manage outer loop (a set of runs)
#


#######################################################################
#
# define output files for metadata and output data
#
#

comment = ''  # add a comment to define your experiment for record. 

ownname = sys.argv[0]
 
git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'])[:10]  # first 10 chars to ID software version

datadir = 'bw_output/'
seqdir  = 'sequences/'

urunid = str(uuid.uuid4())  # a unique hash code for this run 

#if these don't exist, create them 
for ndir in [datadir, seqdir]:
    if not (os.path.exists(os.path.dirname(ndir))):
        os.mkdir(ndir)


metadata_name = 'hmm_bw_metadata.txt'
# Metadata file format:  each line: (comma sep)
#
#  0) date and time stamp
#  1) name of data file
#  2) ownname  (name of the top level file)
#  3) git hash (1st 10 chars of current git hash)
#  4) number of HMM / BT states
#  5) text field (comment)
#
datafile_name = datadir+'data_'+urunid+'.csv'  # a unique filename
# Datafile format:  comma sep
#
#  0)  Task code (2=Baum Welch)
#  1)  Ratio  (codeword mean spacing / sigma)
#  2)  di     (codeword spacing)
#  3)  HMM_delta    amt HMM params changed
#  4)  Sigma
#  5)  run#
#  6)  e2 (RMS error)
#  7)  emax (max error)

sequence_name =  seqdir+'seq_'+urunid+'.txt'   # name of sim sequence file
#
#  sequence file format
#
#  1) true state name
#  2) observation codeword value
#  

fmeta = open(metadata_name, 'a')  #  append metadata to a big log
fdata = open(datafile_name, 'w')  #  unique filename for csv output 
# open sequence_name   in NEWDATA section below 

em = 9999

nsims = 0
e2T = 0.0
emT = 0.0

#print >> fmeta, '-------',datetime.datetime.now().strftime("%y-%m-%d-%H-%M"), 'Nruns: ', Nruns, 'x', NEpochs, ' #states: ',len(names), ' HMM_delta: ',HMM_delta 

##  output the metadata
line = '{:s} | {:s} | {:s} | {:s} | {:d} | {:s}'.format(datetime.datetime.now().strftime("%y-%m-%d-%H:%M"), datafile_name, ownname, git_hash,len(names),  comment)
print >> fmeta , line

#################################################
#
#   Outer Loop
#
for run in range(Nruns):

    print '\n-------------------------------------------\n   Starting Run ',run+1, 'of', Nruns, '\n\n'
    # open the log file
    id = str(int(100*(Ratio)))+'iter'+str(run)  # encode the ratio (delta mu/sigma) into filename
 
    #####    make a string report describing the setup
    #
    #
    rep = []
    rep.append('-------------------------- BT to HMM ---------------------------------------------')
    stringtime = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
    rep.append(stringtime)
    rep.append('NSYMBOLS: {:d}   NEpochs: {:d} N-States: {:d} '.format(NSYMBOLS,NEpochs,len(names)))
    rep.append('sigma: {:.2f}    Symbol delta: {:d}   Ratio:  {:.2f}'.format(sig, int(di), float(di)/float(sig)))
    rep.append('----------------------------------------------------------------------------------')
    rep.append(' ')


    #############################################
    #
    #    Set up models


    #############################################
    #
    #    Build the ABT and its blackboard
    #

    [ABT, bb] = ABTtree()  # defined in xxxxxxABT.py file

    #############################################
    #
    #    Generate Simulated Data only on first round
    #
    if(NEWDATA):
        seq_data_f = open(sequence_name,'w')
        bb.set('logfileptr',seq_data_f)   #allow BT nodes to access file
        osu = names[-2]  # state names
        ofa = names[-1]

        for i in range(NEpochs):
            result = ABT.tick("ABT Simulation", bb)
            if (result == b3.SUCCESS):
                seq_data_f.write('{:s}, {:.0f}\n'.format(osu,outputs[osu]))  # not random obs!
            else:
                seq_data_f.write('{:s}, {:.0f}\n'.format(ofa,outputs[ofa]))
            seq_data_f.write('---\n')

        seq_data_f.close()

        print 'Finished simulating ',NEpochs,'  epochs'

    NEWDATA = False
    #############################################
    #
    #    Read simulated sequence data
    #

    Y = []
    X = []
    Ls = []
    seq_data_f = open(sequence_name,'r')
    [X,Y,Ls] = read_obs_seqs(seq_data_f)
    seq_data_f.close()

    assert len(Y) > 0, 'Empty observation sequence data'

    # remove the old log file
    #os.system('rm '+lfname)

    #############################################
    #
    #    HMM setup
    #
    Ac = A.copy()  # isolate orig A matrix from HMM
    Ar = A.copy()  # reference original copy
    M = HMM_setup(Pi,Ac,sig,names)

    #############################################
    #
    #   Perturb the HMM's parameters (optional)
    #
    #outputAmat(M.transmat_,'Model A matrix',names,sys.stdout)

    A_row_test(M.transmat_, sys.stdout)

    #HMM_ABT_to_random(M)   # randomize probabilites
    #print 'Applied Random Matrix Perturbation'
    HMM_perturb(M, HMM_delta)
    print 'Applied Matrix Perturbation: ' + str(HMM_delta)
    A_row_test(M.transmat_, sys.stdout)

    # special test code
    #  compare the two A matrices
    #     (compute error metrics)
    testeps = 0.00001
    if HMM_delta > testeps: 
        [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(Ar,M.transmat_, names)

        
        ##  some assertions to make sure pertubations are being done right
        #   (if they aren't there's not point in doing the sim)
        assert em > 0.0 , 'Perturbation caused no difference in A matrices'
        assert e2 > 0.0 , 'Perturbation caused no difference in A matrices'
        print 'Model Size: ',len(names)
        if len(names) < 8:
            outS_index = 4
        else:
            outS_index = 14
        outF_index = outS_index+1
        assert M.transmat_[outS_index,outS_index] - 1.0 < testeps, 'A 1.0 element was modified'
        assert M.transmat_[outF_index,outF_index] - 1.0 < testeps, 'A 1.0 element was modified'
    print 'Passed A-matrix Assertions'
    #end of special test code


    A_row_test(M.transmat_, sys.stdout)

    if(task == BaumWelch):
        #############################################
        #
        #   Identify HMM params with Baum-Welch
        #
        print "starting HMM fit with ", len(Y), ' observations.'

        M.fit(Y,Ls)
        # print the output file header
        #for rline in rep:
            #print >>of, rline

        #outputAmat(A,"Original A Matrix", names, of)
        #outputAmat(B,"Perturbed A Matrix", names, of)
        #outputAmat(M.transmat_,"New A Matrix (pertb + HMM fit)", names, of)


        ##  compare the two A matrices
        #     (compute error metrics)
        [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(A,M.transmat_, names)

        #print >> of, 'EAavg    A-matrix error: {:.8f} ({:d} non zero elements)'.format(e2,N2)
        #print >> of, 'EAinfty  A-matrix error: {:.3f} (at {:d} to {:d})'.format(em,im,jm)

        if len(anoms) == 0:
            anoms = 'None'
        #print >> of, 'Anomalies: ', anoms
        if len(erasures) == 0:
            anoms = 'None'
        #print >> of, 'Erasures : ', erasures

        print >>fdata, '{:2d}, {:.3f}, {:3d}, {:.3f}, {:.3f}, {:2d}, {:2d}, {:.3f}, {:.3f}'.format(task, Ratio, int(di), HMM_delta, float(sig), run+1, e2,em)

    nsims += 1
    emT += em
    e2T += e2

#  End of loop of runs

#print >>fdata, '{:3d} {:s} {:.3f}, {:.3f}'.format(task, 'Average e2, em: ',e2T/nsims,emT/nsims)
fdata.close()
fmeta.close()


