#!/usr/bin/python
#
#  tests for logP() package
#

import numpy as np
import numbers
import sys as sys

FAIL = 'FAIL'
PASS = 'PASS'
epsilon = 1.0E-06

from logP import *
from logP_matrix import *

##
#    Important:  use scripts:   set_log_test and set_scale_test prior to this 
#             command.   These scripts choose the desired version of logP() class
#
#    set_log_test: cp logP_log.py logP.py
#        etc/
#
#

print '\n\n  Testing logP() class and related ...\n'

p = logP(0.5)
libname = p.id()  # figure out what type of logP()

print '            Using: ', libname,'\n\n'

e = np.exp(1) 

if (libname == 'log'):
    #####################################
    # test basic log functions

    y = ELv([e, e*e, 0, np.sqrt(e)])

    assert isinstance(y[0], float), 'ELv returns wrong type'
    #print y
    fs = ' elog() test FAIL'
    assert abs(y[0] - 1.0) < epsilon, fs
    assert abs(y[1] - 2.0) < epsilon, fs
    assert np.isnan(y[2]), fs
    assert abs(y[3] - 0.5) < epsilon, fs
    assert abs(ELv(e*e)-2.0) < epsilon, fs
    print 'log only: elog() tests    PASSED'

    # eexp()
    fs = ' eexp() test  FAIL'
    assert  abs(EEv(1)-e) < epsilon, fs
    y = EEv([2, 0, LZ, -1])
    #print y
    assert abs(y[0]-e*e) < epsilon, fs
    assert abs(y[1]-1.0) < epsilon, fs
    assert abs(y[2]-0.0) < epsilon, fs
    assert abs(y[3]-1/e) < epsilon, fs

    assert abs(EEv(1) - e) < epsilon, fs

    y = EEv([[e, 0],[LZ, 1]])
    assert abs(y[1,1]-e) < epsilon, fs
    print 'log only:  eexp() tests    PASSED'

###################################
# test logP classes and operator overloads
x = logP(0.25)
y = logP(0.25)

# make sure stuff returns right types
#print 'x: ', type(x)
assert isinstance(x, logP), 'logP() returns wrong type'
assert abs(x.test_val() - (0.25))< epsilon, 'logP() returns wrong value'
assert abs(x.test_val() - (0.25))< epsilon, 'logP() returns wrong value'

# test with a small constant
z = logP(1.76673447099e-13)
assert isinstance(z, logP), 'logP() returns wrong type'
assert abs(z.test_val() - (1.76673447099e-13))< epsilon, 'logP() returns wrong value'

#  test self initialization
z = logP(x)  # i.e. init with one of its own as argument

assert isinstance(z,logP), 'logP_log: Problem with self initialization'

########################################
#
#   Instantiate some small LogP() entities
#

print 'Python small numbers: '

print '1.0E-900 =', 1.0E-900, ' is an absurdly small number: '
print '1.0E-500 =', 1.0E-500, ' is an absurdly small number: '
print '1.0E-400 =', 1.0E-400, ' is an absurdly small number: '
print '1.0E-321 =', 1.0E-325, ' is an absurdly small number: '
print '1.0E-320 =', 1.0E-320, ' is a very very small number: '
print '1.0E-300 =', 1.0E-300, ' is a very very small number: '
print '1.0E-200 =', 1.0E-200, ' is a very very small number: '
 
print '\n Instantiation of small numbers: '

x_sm_01 = logP(1.0E-300)
x_sm_02 = logP(1.0E-300) 

if(libname == 'scale'):
    print 'scale:  logP(1.0E-300): mant: ', x_sm_01.mant , 'exp: ', x_sm_01.exp
if(libname == 'log'):
    print 'log:    logP(1.0E-300): test_val():', x_sm_01.test_val()
     

if libname=='scale':
    ##################################
    #
    #  test logP_norm()
    #
    x = logP(0.5)
    x.norm()
    fs = '   norm test with '+libname+'   '
    assert abs(x.test_val() - 0.5)<epsilon, fs+FAIL
    x.norm()
    x.norm()
    x.norm()
    assert abs(x.test_val() - 0.5)<epsilon, fs+FAIL
    assert abs(x.exp == 0), fs+FAIL

    x = logP(1.02E-3)
    x.norm()
    assert abs(x.test_val() - 0.00102)<epsilon, fs+FAIL
    x = logP(0.25*0.25)
    x.norm()
    assert abs(x.test_val() - 0.0625)<epsilon, fs+FAIL

    #  test many norm values

    for j in range(50):
        p = (float(j)/200.0) * e*e*e
        x = logP(p)
        x.norm()
        assert abs( p - x.test_val())<epsilon, fs+FAIL

    # test special values
    for x in [1.0, 0.1, 0.01, 0.0001]:
        y = logP(x)
        
        print 'before: ', y.mant, y.exp
        
        y.norm()
        print '  after: ', y.mant, y.exp    
        assert abs(y.test_val() - x)<epsilon, fs+FAIL

    fs1 = 'logP norm, special cases for scale'

    # test some special cases

    a = logP(0.5)
    b = logP(0.5)
    a.exp = -200
    a.mant = 1.7E-05
    b.exp = -400
    b.mant = 3.2E06
    a,b = lPnorm2(a,b)
    
    assert (a.exp == -200), fs1 + FAIL
    assert (a.mant - 1.7E-05)<epsilon, fs1 + FAIL
    assert (b.exp == -200), fs1 + FAIL
    assert (b.mant - 3.2E-194)< epsilon, fs1+FAIL
    
    print fs1+PASS
print fs+PASS

##############################
#
#  logP __add__()

x = logP(0.25)
y = logP(0.25)
z = x + y
assert isinstance(z,logP), 'logP() __add__ returns wrong type'

logsum = np.log(0.25 + 0.25)

fs = 'logP() __add__'
assert abs(z.test_val()-0.500) < epsilon, fs+FAIL
assert abs((x+y).test_val()-0.500) < epsilon, fs+FAIL

# add a scalar

z = logP(0.25) + 0.5
assert abs(z.test_val()-0.750) < epsilon, fs+FAIL


#  infinity tests 
z = x + logP(np.Inf)
assert isinstance(z, logP), fs+FAIL
assert (z.test_val() == np.Inf), fs+FAIL

z = logP(np.Inf) + logP(0.25)
assert isinstance(z, logP), fs+FAIL
assert (z.test_val() == np.Inf), fs+FAIL

z = logP(np.Inf) + logP(np.Inf)
assert isinstance(z, logP), fs+FAIL
assert (z.test_val() == np.Inf), fs+FAIL
    
print fs+PASS

##############################          Multiplication 
#
#  logP __mull__()
#
#   Testing logP() * logp()
print '   Testing Multiplication of logP'
x = logP(0.25)
y = logP(0.25)
z = x * y
assert isinstance(z,logP), 'logP() __mul__ returns wrong type'
prod = 0.25*0.25
logprod = np.log(prod)

fs = 'logP()*logP() __mul__ '
assert abs(z.test_val()-prod) < epsilon, fs+FAIL
assert abs((x*y).test_val()-prod) < epsilon, fs+FAIL
z = x * logP(0)
assert z.test_val() == 0, fs+FAIL
print fs+PASS


#   Testing logP() * float
x = logP(0.25)
y = 4.0
z = x * y
assert isinstance(z,logP), 'logP() * float __mul__ returns wrong type'
prod = 1.0
logprod = np.log(prod)

fs = 'logP()*float __mul__ '
assert abs(z.test_val()-prod) < epsilon, fs+FAIL
assert abs((x*y).test_val()-prod) < epsilon, fs+FAIL 
print fs+PASS


print '     Testing multiplication with underflow'
fs = ' multiplication of very small numbers '
a = logP(1.0E-300) * logP(1.0E-300)

if(libname == 'scale'):
    print 'scale:  logP(1.0E-300)^2: mant: ', a.mant , 'exp: ', a.exp
    assert a.mant == 1.0E-200, fs+FAIL
    assert a.exp  == -400 , fs+FAIL
    
if(libname == 'log'):
    print 'log:    logP(1.0E-300)^2: test_val():', a.test_val()
    assert np.log(a.test_val()) - (-322) < epsilon, fs + FAIL 

print '\n\n'+fs+PASS
print '      Multiplication tests '  + PASS 


fs = ' multiplication of very very very small numbers '

b = a * logP(1.0E-300)

if(libname == 'scale'):
    print 'scale:  logP(1.0E-900): mant: ', b.mant , 'exp: ', b.exp
    assert b.mant == 1.0E-100, fs+FAIL
    assert b.exp  == -800 , fs+FAIL
    
if(libname == 'log'):
    print 'log:    logP(1.0E-300)^2: test_val():', b.test_val()
    assert np.log(b.test_val()) - (-322) < epsilon, fs + FAIL 

print '\n\n'+fs+PASS

quit()
##############################          Division 
#
#  logP __Div__()
#
#   Testing logP() / logp()
print '   Testing Division of logP'
x = logP(0.5)
y = logP(3.0)
z = x / y
assert isinstance(z,logP), 'logP() __div__ returns wrong type'
ans  = 0.5/3.0
logans = np.log(ans)

fs = 'logP() / logP() __div__ '
assert abs(z.test_val()-ans) < epsilon, fs+FAIL
assert abs((x/y).test_val()-ans) < epsilon, fs+FAIL
print fs+PASS


#   Testing logP() / float
x = logP(0.25)
y = 4.0
z = x / y
assert isinstance(z,logP), 'logP() / float __div__ returns wrong type'
ans = 0.25/4.0
logans = np.log(ans)

fs = 'logP() / float __div__ '
assert abs(z.test_val()-ans) < epsilon, fs+FAIL
assert abs((x/y).test_val()-ans) < epsilon, fs+FAIL 
print fs+PASS

#    Testing divide by 0
z = logP(0.25)/0.0
print z, z.test_val()
fs = 'logP() divide by zero '
assert isinstance(z,logP), 'logP() / float __div__ returns wrong type'
assert (z.test_val()==np.Inf), fs+FAIL
print fs+PASS

print '      Division tests '  + PASS 

#############################
#
#  logP += A*B
#

x = logP(0.25)
y = logP(0.25)

t = logP(0.25)

a = t + 0.0625
t = a

fs = 'logP() combined add and times ' + libname + ' version'
assert isinstance(t, logP),fs+FAIL
print a.test_val(), (x*y).test_val()
assert t.test_val() == 0.25*0.25+0.25 ,fs+FAIL



print fs+PASS

print 'logP classes  with ' + libname + '          '+PASS
    
    
    
    
    
####################################################
#  logP for vectors 
#
x = logPv([e, e*e, e*e*e])
y = logPv([e*e, e, 0.001])

fs = 'logPv returns wrong type'
assert isinstance(x[0], logP), fs
assert isinstance(y[2], logP), fs 

fs = 'logPv() instantiation with '+libname+'  '
assert abs(x[0].test_val() - e) < epsilon, fs+FAIL
assert abs(x[1].test_val() - e*e) < epsilon, fs+FAIL
assert abs(x[2].test_val() - e*e*e) < epsilon, fs+FAIL
assert abs(y[0].test_val() -  e*e) < epsilon, fs+FAIL
assert abs(y[1].test_val() - e) < epsilon, fs+FAIL
assert abs(y[2].test_val() - 0.001) < epsilon, fs+FAIL
print fs + PASS

print 'Begin logPv() Setitem tests'

q =logPv([e*e, e, 1/e]) 
q[1] = logP(0.5)


print '\n Test addition of logPv vectors  with '+libname
# let's  sumn two logPv vectors and check them
z = x+y
fs = ' logPv addition produces wrong type'
assert isinstance(z, logPv), fs + FAIL

for i in range(3):
    print ' sum computation: ', x[i],y[i],z[i] 


m = []  # a list of numerical float values
for l in z.v:
    print 'appending ', l, l.test_val()
    m.append(l.test_val())
m = np.array(m)

#print 'm;',m
fs = 'logPv() addition tests '
#print 'compare: ', m[0], (e+e*e)
print 'error: ', abs(m[0] - (e*e+e))
assert abs(m[0] - (e+e*e)) < epsilon, fs + 'FAIL'
print 'error: ', abs(m[1] - (e*e+e))
assert abs(m[1] - (e+e*e)) < epsilon, fs + 'FAIL'
print 'error: ', abs(m[2] - (e*e*e + 1/e))
#assert abs(m[2] - (e*e*e + 0.001)) < epsilon, fs + 'FAIL'

#  logPv add the elements:
x = np.array([[1,2,3,4,5],
              [1,2,3,4,5],
              [1,2,3,4,5],
              [1,2,3,4,5],
              [1,2,3,4,5]   ])
al = logPm(x/10.0)

T = 4
a = logP(0.0) 
print ' adding array elements:'
for j in range(5):
    x = al[T,j]
    print '        ',al[T,j], al[T,j].test_val(), x, x.test_val()
    a = a + x

print a.test_val()
assert a.test_val() == 1.5, fs + libname


print fs + libname+ '         PASS'

###############################################3
#   maxlv() test 
#
v = logPv([0.001, 0.01, 0.5, 4, 0.0])
i, l = v.maxlv()

fs = 'logPv() maxlv()  '

print fs,i, l, l.test_val() 
assert i==3, fs + FAIL
assert abs(l.test_val() - 4.0)<epsilon, fs + FAIL
print fs + PASS


##########################################
#  logPv  __mul__ tests 
#
fs = 'logPv() vector * vector multiply'

x = logPv([e, e*e, e*e*e])
y = logPv([e*e, e, 1/e])

t = x*y
assert abs(t.v[0].test_val() - e*e*e) < epsilon, fs + FAIL
assert abs(t.v[1].test_val() - e*e*e) < epsilon , fs + FAIL
assert abs(t.v[2].test_val() - e*e) < epsilon, fs + FAIL



print '\nlogPv() Tests  ' + PASS

#######################################
#
#   test logPm  - matrix version
#
    #  logP for matrices 
x = logPm(np.array([
        [e, e*e, e*e*e],
        [e, e*e, e*e*e],
        [e, e*e, e*e*e]  ]))

y = logPm(np.array([
        [e*e, e, 1/e],
        [e*e, e, 1/e],
        [e*e, e, 1/e]  ]))

#print '--------------------------'
#print y
#print y[1,0].test_val(),  e*e
#print '--------------------------'

fs = 'logPm returns wrong type'
assert np.shape(x.m) == (3,3), fs
#print x[0,0], type(x.m[0,0])
assert isinstance(x.m[0,0], numbers.Number), fs
assert isinstance(y, logPm), fs
assert isinstance(y[2,1], logP), fs
 
fs = 'logPm() instantiation'

#print y[1,0],  e*e

assert abs(y[1,0].test_val() - e*e)  < epsilon, fs + FAIL
assert abs(y[2,1].test_val() - e)  < epsilon, fs + FAIL
assert abs(y[1,2].test_val() - 1.0/e) < epsilon, fs + FAIL

print fs + PASS

################################################################   TODO:
#
#     Tests for 3D logPm() instances
#

y3 = logPm(np.array(
        [ [
        [e*e, e, 1/e],
        [e*e, e, 1/e],
        [e*e, e, 1/e] ],
        [
        [e*e, e, 1/e],
        [e*e, e, 1/e],
        [e*e, e, 1/e] ],
        [
        [e*e, e, 1/e],
        [e*e, e, 1/e],
        [e*e, e, 1/e] ],
        [
        [e*e, e, 1/e],
        [e*e, e, 1/e],
        [e*e, e, 1/e] ]  ] )
    )
     
###########    add some assertions here

###########   also test math with 3D matrices  

    
print 'Setitem tests'

q =logPm(np.array(
    [
    [e*e, e, 1/e],
    [e*e, e, 1/e],
    [e*e, e, 1/e]  ]
    )) 
q[1,2] = logP(5)

fs = 'logPm setitem() test: '
assert (q[1,2].test_val() -5)<epsilon, fs+FAIL
print fs+PASS

print 'Starting matrix addition tests ...'
z = x + y
assert isinstance(z,logPm), ' logPm() __add__ returns wrong type'


fs = 'EEv(z) matrix argument:  '
assert np.shape(z.m) == (3,3), fs + 'FAIL'

print fs + '             PASS'

#print 'm;',m
fs = 'logPm  __add__() '

assert abs(z[0,0].test_val() - (e+e*e)) < epsilon, fs + 'FAIL'
assert abs(z[0,1].test_val() - (e+e*e)) < epsilon, fs + 'FAIL'
assert abs(z[0,2].test_val() - (e*e*e + 1/e)) < epsilon, fs + 'FAIL'

print fs + '         PASS'


print '   logPm() matrix tests passed\n'
###################################################################
#
#  math combining vector, matrix, getitem, etc.
#

fs = 'logPx mixed math tests'

s = logP(0.5)
v = logPv([1.0, 0.5, 0.25, e])
m = logPm(np.array(
    [[1.0, 0.5, 0.25, e],
     [1.0, 0.5, 0.25, e],
     [1.0, 0.5, 0.25, e]])
    )

n = logPv(np.ones(4))

t = logP(0) + logP(0)
assert abs(t.test_val()-0)<epsilon, fs+FAIL
t = s + v[1]
assert abs(t.test_val() - 1.0)<epsilon, fs+FAIL
t = v[0] + m[1,1]
assert t.test_val() == 1.5, fs+FAIL
t = s + n[2]
assert t.test_val() == 1.5, fs+FAIL
t = logP(0) + n[2]
assert t.test_val()  == 1.0, fs+FAIL
t = logP(0) * n[2]
assert (t.test_val()-0.0)<epsilon, fs+FAIL


print fs+PASS


print '\n\n           logPx() --  ALL TESTS PASS  with '+ libname+'\n\n'

    
