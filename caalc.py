#!/usr/bin/python
# coding: utf

import readline
import sys
import tpg
import itertools

def make_op(s):
    return {
        '+': lambda x,y: x+y,
        '-': lambda x,y: x-y,
        '*': lambda x,y: x*y,
        '/': lambda x,y: x/y,
        '&': lambda x,y: x&y,
        '|': lambda x,y: x|y,
    }[s]

class Vector(list):
    def __init__(self, *argp, **argn):
        list.__init__(self, *argp, **argn)

    def __str__(self):
        #check if vector is matrix
        matrix = True
        for i in xrange(len(self)):
            matrix = matrix and (type(self[i]) == Vector) and (len(self[i]) == len(self[0]))
        if not matrix:
            return "[" + " ".join(str(c) for c in self) + "]"
        else:
            #print matrix in beutiful form
            result = ''
            max = 0
            for i in xrange(len(self)):
                for j in xrange(len(self[i])):
                    if len(str(self[i][j])) > max:
                        max = len(str(self[i][j]))
            max = max + 3
            for i in xrange(len(self)):
                for j in xrange(len(self[i])):
                    result += str(self[i][j]).rjust(max)
                if i < len(self) - 1:
                    result += '\n'
            return result
    def __op(self, a, op):
        try:
            return self.__class__(op(s,e) for s,e in zip(self, a))
        except TypeError:
            return self.__class__(op(c,a) for c in self)

    def __add__(self, a): return self.__op(a, lambda c,d: c+d)
    def __sub__(self, a): return self.__op(a, lambda c,d: c-d)
    def __div__(self, a): return self.__op(a, lambda c,d: c/d)
    def __mul__(self, a): 
        if type(a) != Vector:
            return self.__op(a, lambda c,d: c*d)
        else:
            x = True
            for elem in self:
                x = x and (type(elem) == Vector)
            for elem in a:
                x = x and (type(elem) == Vector)
            if not x:
                raise TypeError, "Error: Incorrect matrix 1"
            x = True
            for elem in self:
                x = x and (len(elem) == len(self[0]))
            for elem in a:
                x = x and (len(elem) == len(a[0]))
            if not x:
                raise TypeError, "Error: Incorrect matrix 2"
            
            if len(self[0]) != len(a):
                raise TypeError, "Error: Matrix multiplication impossible"
            transposed_a = zip(*a)
            return Vector([ Vector ([ reduce(lambda x, y: x+y, map(lambda pair: pair[0]*pair[1], zip(self[i1], transposed_a[i2]))) for i2 in xrange(len(a[0]))])for i1 in xrange(len(self))])

    def __and__(self, a):
        try:
            return reduce(lambda s, (c,d): s+c*d, zip(self, a), 0)
        except TypeError:
            return self.__class__(c and a for c in self)

    def __or__(self, a):
        try:
            return self.__class__(itertools.chain(self, a))
        except TypeError:
            return self.__class__(c or a for c in self)

class Calc(tpg.Parser):
    r"""

    separator spaces: '\s+' ;
    separator comment: '#.*' ;

    token fnumber: '\d+[.]\d*' float ;
    token number: '\d+' int ;
    token op1: '[|&+-]' make_op ;
    token op2: '[*/]' make_op ;
    token finish: 'exit' ;
    token id: '\w+' ;

    START/e -> finish $ global Stop; Stop=True; e=None $ | Operator $e=None$ | Expr/e | $e=None$ ;
    Operator -> Assign ;
    Assign -> id/i '=' Expr/e $Vars[i]=e$ ;
    Expr/t -> Fact/t ( op1/op Fact/f $t=op(t,f)$ )* ;
    Fact/f -> Atom/f ( op2/op Atom/a $f=op(f,a)$ )* ;
    Atom/a -> Vector/a
              | id/i ( check $i in Vars$ | error $"Undefined variable '{}'".format(i)$ ) $a=Vars[i]$
              | fnumber/a
              | number/a
              | '\(' Expr/a '\)' ;
    Vector/$Vector(a)$ -> '\[' '\]' $a=[]$ | '\[' Atoms/a '\]' ;
    Atoms/v -> Atom/a Atoms/t $v=[a]+t$ | Atom/a $v=[a]$ ;

    """

calc = Calc()
Vars={}
PS1='--> '

print "Welcome to calc. Type 'exit' or press Ctrl + D to leave"

Stop=False
clst = []

while not Stop:
    if len(clst):
    	line = clst[0]
        print PS1, line
        clst = clst[1:]
    else:
        try:
            line = raw_input(PS1)
        except EOFError:
            break
        if line[:4] == 'file':
            try:
                src = open(line[5:])
                clst = list(src.read().split('\n'))
                continue
            except:
                print 'Error: Something wrong with file'
                continue
    try:
        res = calc(line)
    except tpg.Error as exc:
        print >> sys.stderr, exc
        res = None
    except TypeError as exc:
        print exc
        res = None
    if res != None:
        print res
