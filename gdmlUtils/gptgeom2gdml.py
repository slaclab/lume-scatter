#!/usr/bin/python
# Sat Apr  9 09:26:54 AM PDT 2022
# **************************************************************************
# *                                                                        *
# *   Copyright (c) 2021 Munther Hindi
# *                                                                        *
# *   This program is free software; you can redistribute it and/or modify *
# *   it under the terms of the GNU Lesser General Public License (LGPL)   *
# *   as published by the Free Software Foundation; either version 2 of    *
# *   the License, or (at your option) any later version.                  *
# *   for detail see the LICENCE text file.                                *
# *                                                                        *
# *   This program is distributed in the hope that it will be useful,      *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of       *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        *
# *   GNU Library General Public License for more details.                 *
# *                                                                        *
# *   You should have received a copy of the GNU Library General Public    *
# *   License along with this program; if not, write to the Free Software  *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 *
# *   USA                                                                  *
# *                                                                        *
# *   Acknowledgements : Export to gdml code partially copied from         *
# *                      https://github.com/KeithSloan/GDML                *
# *                                                                        *
# ***************************************************************************

import os.path
import sys
import re
import numpy as np
import math

# ######################## ply parser ###################################
reserved = (
    'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
    'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh',
    'log', 'Log10', 'Log2', 'Log1p', 'exp', 'exp2', 'expm1',
    'sqrt', 'cbrt', 'abs', 'ceil', 'floor', 'round', 'trunc',
    'erf', 'erfc', 'tgamma', 'lgamma', 'number', 'string',
)

tokens = reserved + (
    'SKIP', 'VARIABLE', 'NUMBER', 'COMMENT', 'STRING', 'ISTRING',
    'ZSTRING', 'scatterer',
)

literals = ['=', '+', '-', '*', '/', '(', ')',
            ';', '^', '"', ',', ]


# Tokens

def t_SKIP(t):
    '''(set.*\(.*\).*)|
       (add.*\(.*\).*)|
       (acceptance.*\(.*\).*)|
       (accuracy.*\(.*\).*)|
       (dtmax.*\(.*\).*)|
       (outputvalue.*\(.*\).*)|
       (pp.*\(.*\).*)|
       (screen.*\(.*\).*)|
       (snapshot.*\(.*\).*)|
       (tcontinue.*\(.*\).*)|
       (tout.*\(.*\).*)|
       (write.*\(.*\).*)|
       (TE.*\(.*\).*)|
       (TM.*\(.*\).*)|
       (trw.*\(.*\).*)|
       (ecyl.*\(.*\).*)|
       (ehole.*\(.*\).*)|
       (erect.*\(.*\).*)|
       (.*charge.*\(.*\.*)|
       (barmagnet.*\(.*\).*)|
       (Bmultipole.*\(.*\).*)|
       (bzsolenoid.*\(.*\).*)|
       (isectormagnet.*\(.*\.*)|
       (linecurrent.*\(.*\).*)|
       (mag.*\(.*\).*)|
       (quadrupole.*\(.*\).*)|
       (rect.*\(.*\).*)|
       (sectormagnet\(.*\).*)|
       (sextuplole\(.*\).*)|
       (solenoid\(.*\).*)|
       ([mM]?ap.*\(.*\).*)|
       (spacecharge.*\(.*\).*)|
       (zminmax\(.*\).*)|
       (forwardscatter\(.*\).*)|
       (copperscatter\(.*\).*)|
       (geant4scatter\(.*\).*)|
       (random\(.*\))'''

    print(f'skipping {t.value}')
    # t.lexer.lineno += t.value.count('\n')


def t_scatterer(t):
    r'scatter[a-z]+'
    return t


def t_ISTRING(t):
    r'\"I\"'
    return t


def t_ZSTRING(t):
    r'\"z\"'
    return t


def t_STRING(t):
    r'\"[a-zA-Z0-9_]+\"'
    return t


def t_COMMENT(t):
    r'[#].*'
    return t


def t_NUMBER(t):
    r'[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'
    # r'\d*)?\.?\d*(e(\+|\-)\d+)?'
    # r'((\d+)(\.\d+)(e(\+|\-)?(\d+))?'
    t.value = float(t.value)
    return t


t_ignore = " \t"


def t_tanh(t):
    r'tanh'
    return t


def t_cosh(t):
    r'cosh'
    return t


def t_sinh(t):
    r'sinh'
    return t


def t_sin(t):
    r'sin'
    return t


def t_cos(t):
    r'cos'
    return t


def t_tan(t):
    r'tan'
    return t


def t_asinh(t):
    r'asinh'
    return t


def t_asin(t):
    r'asin'
    return t


def t_acosh(t):
    r'acosh'
    return t


def t_acos(t):
    r'acos'
    return t


def t_atanh(t):
    r'atanh'
    return t


def t_atan(t):
    r'atan'
    return t


def t_log(t):
    r'log'
    return t


def t_Log10(t):
    r'Log10'
    return t


def t_Log2(t):
    r'Log2'
    return t


def t_Log1p(t):
    r'Log1p'
    return t


def t_exp2(t):
    r'exp2'
    return t


def t_expm1(t):
    r'expm1'
    return t


def t_exp(t):
    r'exp'
    return t


def t_sqrt(t):
    r'sqrt'
    return t


def t_cbrt(t):
    r'cbrt'
    return t


def t_abs(t):
    r'abs'
    return t


def t_ceil(t):
    r'ceil'
    return t


def t_floor(t):
    r'floor'
    return t


def t_round(t):
    r'round'
    return t


def t_trunc(t):
    r'trunc'
    return t


def t_erfc(t):
    r'erfc'
    return t


def t_erf(t):
    r'erf'
    return t


def t_tgamma(t):
    r'tgamma'
    return t


def t_lgamma(t):
    r'lgamma'
    return t


def t_number(t):
    r'number'
    return t


def t_string(t):
    r'string'
    return t


def t_VARIABLE(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lex.lex()

# Parsing rules

precedence = (
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
    ('right', '^'),
)

# dictionary of variables
variables = {}
variables['c'] = 299792458.0
variables['deg'] = 180/math.pi
variables['e'] = math.exp(1.0)
variables['eps0'] = 8.8541878128e-12
variables['me'] = 9.1093837015e-31
variables['ma'] = 1.660539066e-27
variables['mp'] = 1.672621923e-27
variables['mu0'] = 4*math.pi*1e-7
variables['pi'] = math.pi
variables['qe'] = -1.602176634e-19
variables['q'] = variables['qe']
variables['m'] = variables['me']


def p_statement(p):
    '''statement : 
                 | statement_comment
                 | statement_assign
                 | statement_assign statement_comment
                 | statement_scatter
                 | statement_scatter statement_comment
    '''

def p_statement_comment(p):
    '''statement_comment : COMMENT '''
    processPseudoinfo(p[1])


def p_statement_assign(p):
    """statement_assign : VARIABLE '=' expression ';' """
    variables[p[1]] = p[3]
    print([p[1]], variables[p[1]])


def p_statement_scatter(p):
    """ statement_scatter : scatterfunc VARIABLE '=' STRING ';' """


def p_expression_function(p):
    """expression : sin '(' expression ')' 
                  | cos '(' expression ')'
                  | tan '(' expression ')'
                  | asin '(' expression ')'
                  | acos '(' expression ')'
                  | atan '(' expression ')'
                  | sinh '(' expression ')'
                  | cosh '(' expression ')'
                  | tanh '(' expression ')'
                  | asinh '(' expression ')'
                  | acosh '(' expression ')'
                  | atanh '(' expression ')'
                  | log '(' expression ')'
                  | Log10 '(' expression ')'
                  | Log2 '(' expression ')'
                  | Log1p '(' expression ')'
                  | exp '(' expression ')'
                  | exp2 '(' expression ')'
                  | expm1 '(' expression ')'
                  | sqrt '(' expression ')'
                  | cbrt '(' expression ')'
                  | abs '(' expression ')'
                  | ceil '(' expression ')'
                  | floor '(' expression ')'
                  | round '(' expression ')'
                  | trunc '(' expression ')'
                  | erf '(' expression ')'
                  | erfc '(' expression ')'
                  | tgamma '(' expression ')'
                  | lgamma '(' expression ')'
                  | number '(' STRING ')'
                  | string '(' expression ')'"""
    from math import sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh, \
        log, log10, log2, log1p, exp, expm1, sqrt, fabs, ceil, floor, trunc, erf, erfc, gamma, lgamma
    from numpy import log1p
    
    func = p[1]
    if p[1] == 'Log10':
        func = 'log10'
    elif p[1] == 'Log2':
        func = 'log2'
    elif p[1] == 'Log1p':
        func = 'log1p'
    elif p[1] == 'exp2':
        p[0] = pow(2, p[3])
        return
    elif p[1] == 'cbrt':
        p[0] = pow(p[3], 1./3.)
        return
    elif p[1] == 'abs':
        func = 'fabs'
    elif p[1] == 'tgamma':
        func = 'gamma'
    elif p[1] == 'number':
        p[0] = str(p[3])
        return
    elif p[1] == 'string':
        p[0] = float(p[3])
        return

    expr = func + '(' + str(p[3]) + ')'
    p[0] = eval(expr)
    print(f'mathfunc {p[0]}')


def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression
                  | expression '^' expression'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]
    elif p[2] == '^':
        n = int(p[3])
        prod = 1.0
        for i in range(0, n):
            prod *= p[1]
        p[0] = prod


def p_expression_number(p):
    "expression : NUMBER "
    p[0] = p[1]


def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]


def p_expression_group(p):
    "expression : '(' expression ')'"
    p[0] = p[2]


def p_expression_name(p):
    "expression : VARIABLE"
    try:
        p[0] = variables[p[1]]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0


def p_scatterfunc(p):
    """scatterfunc : scatterer '(' arg_list ')'
    """
    args = p[3]
    sargs = ''
    for s in args:
        sargs += str(s)
    line = p[1] + '(' + sargs + ')'
    print(f'p_scatterfunc {line}')
    processScatterLine(line)


def p_arg_list_1(p):
    """arg_list : ECS 
    """
    p[0] = p[1]
    print(f'arg_list_1 {p[0]}')


def p_arg_list_2(p):
    """arg_list : arg_list ',' expression_list
    """
    p[0] = p[1] + p[2] + p[3]
    print(f'arg_list_2 {p[0]}')


def p_expression_list_1(p):
    """expression_list : expression
    """
    p[0] = str(p[1])


def p_expression_list_2(p):
    """expression_list : expression_list ',' expression
    """
    p[0] = p[1] + p[2] + str(p[3])


def p_ECS(p):
    """ECS : STRING ',' ISTRING
           | STRING ',' ZSTRING ',' expression
           | STRING ',' expression ',' expression ',' expression ',' expression ',' expression ',' expression
    """
    if len(p) == 4:
        p[0] = p[1] + p[2] + p[3]
    elif len(p) == 6:
        p[0] = p[1] + p[2] + p[3] + p[4] + str(p[5])
    else:
        s = p[1]
        for i in range(2, len(p)):
            s += p[i]
            p[0] = s
    print(f'arg {p[0]}')


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


import ply.yacc as yacc
yacc.yacc()

# ################################ end ply yacc ##############################

import lxml.etree as ET
# import xml.etree.ElementTree as ET

global zOrder
defaultThickness = 4.0  # defaultThickness of scatter elements
# defaultMaterial = "G4_Cu"
defaultMaterial = "G4_STAINLESS-STEEL"
# irisThickness = 0.1 # mm

colors = ["#FF930080", "#007DFF80", "#FF320080", "#00CAFF80", "#B281FF80",
          "#C8FF8180"]
num_colors = len(colors)
color_index = 0

if len(sys.argv) != 3:
    print("usage: gptgeom2gdml <inputfile> <outputFile>")
    exit(1)

filename = sys.argv[1]
outFile = sys.argv[2]


#################################
# Switch functions
################################
class switch(object):
    value = None

    def __new__(class_, value):
        class_.value = value
        return True


def case(*args):
    return any((arg == switch.value for arg in args))

# ########################################################
# Pretty format GDML                                    #
# ########################################################
def indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem


def standardMaterials():
    item = ET.SubElement(materials, 'material', {'name': "Cu",
                                                 'Z': "27.0"})
    ET.SubElement(item, 'D', {'value': "8.96"})
    ET.SubElement(item, 'atom', {'value': "63.546"})

    item = ET.SubElement(materials, 'material', {'name': "Al",
                                                 'Z': "13.0"})
    ET.SubElement(item, 'D', {'value': "2.70"})
    ET.SubElement(item, 'atom', {'value': "26.98"})

    item = ET.SubElement(materials, 'material', {'name': "STAINLESS-STEEL",
                                                 'formula': "STAINLESS-STEEL"})
    ET.SubElement(item, 'D', {'value': "8"})
    ET.SubElement(item, 'fraction', {'n': "0.169001", 'ref': "G4_Cr"})
    ET.SubElement(item, 'fraction', {'n': "0.746213", 'ref': "G4_Fe"})
    ET.SubElement(item, 'fraction', {'n': "0.0847861", 'ref': "G4_Ni"})

#################################
#  Setup GDML environment
#################################
def GDMLstructure():
    print("Setup GDML structure")
    #################################
    # globals
    ################################
    global gdml, define, materials, solids, structure, setup, worldVOL
    global defineCnt, LVcount, PVcount, POScount, ROTcount
    global CONEcount, CYLINDERcount, BOXcount, SPHEREcount, TORUScount
    global lineNumber

    defineCnt = LVcount = PVcount = POScount = ROTcount = 1
    CONEcount = CYLINDERcount = BOXcount = SPHEREcount = TORUScount = 1
    lineNumber = 1

    gdml = initGDML()
    define = ET.SubElement(gdml, 'define')
    materials = ET.SubElement(gdml, 'materials')
    solids = ET.SubElement(gdml, 'solids')
    structure = ET.SubElement(gdml, 'structure')
    setup = ET.SubElement(gdml, 'setup', {'name': 'Default', 'version': '1.0'})
    # worldVOL = None
    # worldVOL needs to be added after file scanned.
    # ET.ElementTree(gdml).write("/tmp/test2", 'utf-8', True)
    ET.SubElement(define, 'position', {'name': 'origin', 'unit': 'mm',
                                       'x': '0', 'y': '0', 'z': '0'})
    ET.SubElement(define, 'rotation', {'name': 'identity', 'unit': 'deg',
                                       'x': '0', 'y': '0', 'z': '0'})

    standardMaterials()

    return structure


def exportGDML(filepath):

    indent(gdml)
    print("Write to gdml file")
    # ET.ElementTree(gdml).write(filepath, 'utf-8', True)
    # ET.ElementTree(gdml).write(filepath, xml_declaration=True)
    ET.ElementTree(gdml).write(filepath, pretty_print=True,
                               xml_declaration=True)
    print("GDML file written")


def rotMatrix(xx, xy, xz, yx, yy, yz):
    xp = np.array((xx, xy, xz))
    yp = np.array((yx, yy, yz))
    x = xp/np.sqrt(np.dot(xp, xp))
    y = yp/np.sqrt(np.dot(yp, yp))
    z = np.cross(x, y)
    R = np.array(((x[0], y[0], z[0]),
                  (x[1], y[1], z[1]),
                  (x[2], y[2], z[2])))
    return R


def exportPosition(name, xml, pos):
    x = pos[0]
    y = pos[1]
    z = pos[2]
    posName = 'P-'+name
    posxml = ET.SubElement(define, 'position', {'name': posName,
                                                'unit': 'mm'})
    if x != 0:
        posxml.attrib['x'] = str(x)
    if y != 0:
        posxml.attrib['y'] = str(y)
    if z != 0:
        posxml.attrib['z'] = str(z)
    ET.SubElement(xml, 'positionref', {'ref': posName})


def exportRotation(name, xml, angles):
    a0 = angles[0]
    a1 = angles[1]
    a2 = angles[2]
    if a0 != 0 or a1 != 0 or a2 != 0:
        rotName = 'R-'+name+str(ROTcount)
        rotxml = ET.SubElement(define, 'rotation', {'name': rotName,
                                                    'unit': 'deg'})
        if abs(a0) != 0:
            rotxml.attrib['x'] = str(-a0)
        if abs(a1) != 0:
            rotxml.attrib['y'] = str(-a1)
        if abs(a2) != 0:
            rotxml.attrib['z'] = str(-a2)
        ET.SubElement(xml, 'rotationref', {'ref': rotName})

#
# Given Matrix R
# return rotation angles az, ay, az, in degrees
#
# This is my derivation;
#
# R = Rz(az) Ry(ay) Rz(ax)
#
# Where the rotation matrices are:
#       [ cos(az)  -sin(az)   0]
#  Rz = [ sin(az)   cos(az)   0|
#       [    0         0      1]
#
#       [ cos(ay)      0   sin(ay) ]
#  Ry = [    0         1       0   |
#       [-sin(ay)      0   cos(ay) ]
#
#       [    0         0      1         ]
#  Rx = [    0      cos(ax)   -sin(ax)  |
#       [    0      sin(ax)    cos(ax)  ]
#
# x = (1,0,0), y=(0,1,0), z=(0,0,1) be unit vectors along respective axes
#
# then
# sin(ay) = -zT R x
# cos(ay) sin(az) = zT R y, where zT is transpose of column vector x
# cos(ay) cos(az) = zT R z
# and az = atan2( zT R x, zT R y )
# and
# cos(ay) = zT R y sin(az) + zT R z cos(az)
# and
#  ay = atan2(sin(ay), cos(ay))
#
# Then
#
#  Rx(ax) = Ry^-1 Rz^-1 R
#
# and ax = atan2( Rx[2][1], Rx[2][2] )
#
# The inverse matrices are
# Ry^-1 = Ry(-ay)
# Rz^-1 = Rz(-az)
#
def rotAngles(R):
    x = np.array((1, 0, 0))
    y = np.array((0, 1, 0))
    z = np.array((0, 0, 1))
    sinay = -np.dot(z, np.dot(R, x))
    cosay_sinaz = np.dot(z, np.dot(R, y))
    cosay_cosaz = np.dot(z, np.dot(R, z))
    az = np.atan2(cosay_sinaz, cosay_cosaz)
    cosay = cosay_sinaz * np.sin(az) + cosay_cosaz
    ay = np.arctan2(sinay, cosay)

    Ryinv = np.array(((np.cos(ay), 0, -np.sin(ay)),
                      (0, 1, 0),
                      (np.sin(ay), 0, np.cos(ay))))
    Rzinv = np.array(((np.cos(az), -np.sin(az), 0),
                      (np.sin(az),  np.cos(az), 0),
                      (0, 0, 1)))
    Rx = np.dot(Ryinv, np.dot(Rzinv, R))
    ax = np.arctan2(Rx[2][1], Rx[2][2])

    return [np.degrees(ax), np.degrees(ay), np.degrees(az)]


def getECSandArgs(args, zoffset=0):
    global POScount, ROTcount

    words = args.split(",")
    ECSname = words[0]
    ECStype = words[1]

    if ECStype == "\"I\"":  # identity transform
        return {"posRef": "origin",
                "rotRef": "identity",
                "args": words[2:]}
    elif ECStype == "\"z\"":  # translation along z
        z = 1000.0*float(words[2])  # convert to mm
        if z > 0:
            z += zoffset
        else:
            z -= zoffset
        posName = "POS{}".format(POScount)
        POScount += 1
        ET.SubElement(define, 'position', {'name': posName, 'unit': 'mm',
                                           'x': '0', 'y': '0', 'z': str(z)})
        return {'posRef': posName, 'rotRef': "identity", 'args': words[3:]}
    else:  # general transformation
        ox = 1000.0*float(words[1])  # convert meters to mm
        oy = 1000.0*float(words[2])  # convert meters to mm
        oz = 1000.0*float(words[3])  # convert meters to mm
        if oz > 0:
            oz += zoffset
        else:
            oz -= zoffset
        posName = "POS{}".format(POScount)
        POScount += 1
        ET.SubElement(define, 'position', {'name': posName, 'unit': 'mm',
                                           'x': str(ox), 'y': str(oy), 'z': str(oz)})
        xx = float(words[4])
        xy = float(words[5])
        xz = float(words[6])
        yx = float(words[7])
        yy = float(words[8])
        yz = float(words[9])

        R = rotMatrix(xx, xy, xz, yx, yy, yz)
        ax, ay, az = rotAngles(R)
        rotName = "ROT{}".format(ROTcount)
        ROTcount += 1
        ET.SubElement(define, 'rotation', {'name': rotName, 'unit': 'deg',
                                           'x': str(ax), 'y': str(ay), 'z': str(az)})
        return {'posRef': posName, 'rotRef': rotName, 'args': words[11:]}


def getConeECSandArgs(args):
    global POScount, ROTcount

    words = args.split(",")
    ECSname = words[0]
    ECStype = words[1]

    if ECStype == '"I"':  # identity transform
        z1 = float(words[2]) * 1000
        R1 = float(words[3]) * 1000
        z2 = float(words[4]) * 1000
        R2 = float(words[5]) * 1000
        height = (z2 - z1)
        oz = z1 + height/2  # of midpoint
        posName = "POS{}".format(POScount)
        POScount += 1
        ET.SubElement(define, 'position', {'name': posName, 'unit': 'mm',
                                           'x': '0', 'y': '0', 'z': str(oz)})
        return {"posRef": posName,
                "rotRef": "identity",
                "args": [R1, R2, height]}

    elif ECStype == '"z"':  # translation along z
        z = 1000.0*float(words[2])  # convert to mm
        posName = "POS{}".format(POScount)
        POScount += 1
        z1 = float(words[3]) * 1000
        R1 = float(words[4]) * 1000
        z2 = float(words[5]) * 1000
        R2 = float(words[6]) * 1000
        height = (z2 - z1)
        oz = z + z1 + height/2  # of midpoint

        ET.SubElement(define, 'position', {'name': posName, 'unit': 'mm',
                                           'x': '0', 'y': '0', 'z': str(oz)})
        return {'posRef': posName, 'rotRef': "identity",
                'args': [R1, R2, height]}

    else:  # general transformation
        ox = 1000.0*float(words[1])  # convert meters to mm
        oy = 1000.0*float(words[2])  # convert meters to mm
        oz = 1000.0*float(words[3])  # convert meters to mm
        posName = "POS{}".format(POScount)
        POScount += 1
        z1 = float(words[10]) * 1000
        R1 = float(words[11]) * 1000
        z2 = float(words[12]) * 1000
        R2 = float(words[13]) * 1000
        height = (z2 - z1)
        oz += z1 + height/2  # of midpoint
        ET.SubElement(define, 'position', {'name': posName, 'unit': 'mm',
                                           'x': str(ox), 'y': str(oy), 'z': str(oz)})
        xx = float(words[4])
        xy = float(words[5])
        xz = float(words[6])
        yx = float(words[7])
        yy = float(words[8])
        yz = float(words[9])

        R = rotMatrix(xx, xy, xz, yx, yy, yz)
        ax, ay, az = rotAngles(R)
        rotName = "ROT{}".format(ROTcount)
        ROTcount += 1
        ET.SubElement(define, 'rotation', {'name': rotName, 'unit': 'deg',
                                           'x': str(ax), 'y': str(ay), 'z': str(az)})
        return {'posRef': posName, 'rotRef': rotName,
                'args': [R1, R2, height]}


def getPipeECSandArgs(args):
    global POScount, ROTcount

    words = args.split(",")
    ECSname = words[0]
    ECStype = words[1]

    if ECStype == '"I"':  # identity transform
        z1 = float(words[2]) * 1000
        z2 = float(words[3]) * 1000
        R1 = float(words[4]) * 1000
        height = (z2 - z1)
        oz = z1 + height/2  # of midpoint
        posName = "POS{}".format(POScount)
        POScount += 1
        ET.SubElement(define, 'position', {'name': posName, 'unit': 'mm',
                                           'x': '0', 'y': '0', 'z': str(oz) })
        return {"posRef": posName,
                "rotRef": "identity",
                "args": [R1, height]}

    elif ECStype == '"z"':  # translation along z
        z = 1000.0*float(words[2])  # convert to mm
        posName = "POS{}".format(POScount)
        POScount += 1
        z1 = float(words[3]) * 1000
        z2 = float(words[4]) * 1000
        R1 = float(words[5]) * 1000
        height = (z2 - z1)
        oz = z + z1 + height/2  # of midpoint

        ET.SubElement(define, 'position', {'name': posName, 'unit': 'mm',
                                           'x': '0', 'y': '0', 'z': str(oz) })
        return {'posRef': posName, 'rotRef': "identity",
                'args': [R1, height]}

    else:  # general transformation
        ox = 1000.0*float(words[1])  # convert meters to mm
        oy = 1000.0*float(words[2])  # convert meters to mm
        oz = 1000.0*float(words[3])  # convert meters to mm
        posName = "POS{}".format(POScount)
        POScount += 1
        z1 = float(words[10]) * 1000
        z2 = float(words[11]) * 1000
        R1 = float(words[12]) * 1000
        height = (z2 - z1)
        oz += z1 + height/2  # of midpoint
        ET.SubElement(define, 'position', {'name': posName, 'unit': 'mm',
                                           'x': str(ox), 'y': str(oy), 'z': str(oz)})
        xx = float(words[4])
        xy = float(words[5])
        xz = float(words[6])
        yx = float(words[7])
        yy = float(words[8])
        yz = float(words[9])

        R = rotMatrix(xx, xy, xz, yx, yy, yz)
        ax, ay, az = rotAngles(R)
        rotName = "ROT{}".format(ROTcount)
        ROTcount += 1
        ET.SubElement(define, 'rotation', {'name': rotName, 'unit': 'deg',
                                           'x': str(ax), 'y': str(ay), 'z': str(az)})
        return {'posRef': posName, 'rotRef': rotName,
                'args': [R1, height]}


def processGDMLCone(args):
    global lineNumber
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    coneName = "Cone_{}".format(lineNumber)
    rmin1 = args[0]
    rmin2 = args[1]
    height = args[2]
    rmax1 = rmin1 + defaultThickness
    rmax2 = rmin2 + defaultThickness
    if rmax1 > rmax2:
        rmax2 = rmax1
    else:
        rmax1 = rmax2
    startphi = 0
    deltaphi = 360
    ET.SubElement(solids, 'cone', {'name': coneName,
                                   'rmin1': str(rmin1),
                                   'rmin2': str(rmin2),
                                   'rmax1': str(rmax1),
                                   'rmax2': str(rmax2),
                                   'startphi': str(startphi),
                                   'deltaphi': str(deltaphi),
                                   'aunit': "deg",
                                   'z': str(height),
                                   'lunit': 'mm'})
    return(coneName)


def processIRIS(args):
    global lineNumber
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    cylName = "Tube_{}".format(lineNumber)
    rmin = args[0]
    rmax = args[1]
    height = args[2]
    startphi = 0
    deltaphi = 360
    ET.SubElement(solids, 'tube', {'name': cylName,
                                   'rmin': str(rmin),
                                   'rmax': str(rmax),
                                   'startphi': str(startphi),
                                   'deltaphi': str(deltaphi),
                                   'aunit': "deg",
                                   'z': str(height),
                                   'lunit': 'mm'})

    return(cylName)


def torusCone(name, radius, angle):
    from math import pi
    if pi/2 < angle < pi:
        angle = pi - angle
    elif pi < angle < 3.*pi/2:
        angle = angle - pi
    elif 3.*pi/2 < angle < 2*pi:
        angle = 2*pi - angle

    rmin1 = 0
    rmax1 = 2*radius
    rmin2 = 0
    rmax2 = 0
    z = rmax1/np.tan(angle)
    solid = ET.SubElement(solids, 'cone', {'name': name,
                                           'rmin1': str(rmin1),
                                           'rmin2': str(rmin2),
                                           'rmax1': str(rmax1),
                                           'rmax2': str(rmax2),
                                           'startphi': '0',
                                           'deltaphi': '360',
                                           'aunit': "deg",
                                           'z': str(z),
                                           'lunit': 'mm'})
    return solid


def torus(name, rin, rtor):

    ET.SubElement(solids, 'torus', {'name': name,
                                    'rmin': str(rin),
                                    'rmax': str(rin+defaultThickness),
                                    'rtor': str(rtor),
                                    'startphi': '0',
                                    'deltaphi': '360',
                                    'aunit': 'deg',
                                    'lunit': 'mm'})


def tube(name, rmin, rmax, z):
    startphi = 0
    deltaphi = 360
    solid = ET.SubElement(solids, 'tube', {'name': name,
                                           'rmin': str(rmin),
                                           'rmax': str(rmax),
                                           'startphi': str(startphi),
                                           'deltaphi': str(deltaphi),
                                           'aunit': "deg",
                                           'z': str(z),
                                           'lunit': 'mm'})

    return solid


def A_minus_B(name, A, B):
    solid = ET.SubElement(solids, 'subtraction', {'name': name})
    ET.SubElement(solid, 'first', {'ref': A})
    ET.SubElement(solid, 'second', {'ref': B})
    return solid


def A_plus_B(name, A, B):
    solid = ET.SubElement(solids, 'union', {'name': name})
    ET.SubElement(solid, 'first', {'ref': A})
    ET.SubElement(solid, 'second', {'ref': B})
    return solid


def A_intersection_B(name, A, B):
    solid = ET.SubElement(solids, 'intersection', {'name': name})
    ET.SubElement(solid, 'first', {'ref': A})
    ET.SubElement(solid, 'second', {'ref': B})
    return solid


def snapToQuadrant(angle):
    eps = 1e-4
    # if angle is withing eps from 0, pi/2, pi, 3pi/2 or 2pi
    # snape tp those angles
    if np.fabs(angle) < eps:
        angle = 0
    if np.fabs(angle-np.pi/2) < eps:
        angle = np.pi/2
    if np.fabs(angle-np.pi) < eps:
        angle = np.pi
    if np.fabs(angle-3./2.*np.pi) < eps:
        angle = 3./2.*np.pi
    if np.fabs(angle-2*np.pi) < eps:
        angle = 2*np.pi

    return angle


def torusSection(sectionName, angle, rin, rtor):
    # Build torus section from angle to 2pi
    # Need to cut the torus by cones, boxes, or tubes;
    # Except for when then angle involved is 0, pi/2, pi, 3/2 pi or 2*pi
    # A cutting  surface is represent by a cone. If the angle is in the 1st or 3d quadrant
    # the cone vertex is on the -z side. If the angle is in the 2nd or 4th quadrant
    # the cone vertex is on the +z side and the cone has to be rotated by 180 degrees
    # about the x-axis (y-axis could have been used also).
    # To help with the geometry, we also introudce a tube, with  radius = rtor
    # for the special cases of angles =0, pi/2, pi, 3/2 pi and 2pi, the cones
    # are replaced by tubes.
    #
    # returns: name of solid built, None if no solid is built
    #
    torusBool = sectionName+'_bool'
    torusSolid = torus(torusBool, rin, rtor)
    tubeName = sectionName+'_tube'
    height = 2.2*rin
    tubeSolid = tube(tubeName, 0, rtor, height)
    coneName = sectionName+'_cone'
    if angle != 0 and angle != np.pi/2 and angle != np.pi and angle != 3./2.*np.pi and angle != 2*np.pi:
        coneSolid = torusCone(coneName, rtor, angle)

    if angle == 0:
        return torusBool
    elif 0 < angle < np.pi/2:
        notCone = 'not'+coneName
        solid = A_minus_B(notCone, torusBool, coneName)
        exportRotation(notCone, solid, [180, 0, 0])
        name = 'union_'+tubeName+'_'+notCone
        intersection = 'intersect_'+tubeName
        A_intersection_B(intersection, tubeName, torusBool)
        A_plus_B(sectionName, notCone, intersection)
    elif angle == np.pi/2:
        outTubeName = 'outer_'+tubeName
        tube(outTubeName, rtor, rtor+2.2*rin, height)
        solid = A_minus_B(sectionName, torusBool, outTubeName)
        exportPosition(outTubeName, solid, [0, 0, height/2])
    elif np.pi/2 < angle < np.pi:
        intersection1 = 'intersection_'+coneName
        A_intersection_B(intersection1, torusBool, coneName)
        intersection2 = 'intersection_'+tubeName
        A_intersection_B(intersection2, torusBool, tubeName)
        A_plus_B(sectionName, intersection1, intersection2)
    elif angle == np.pi:
        A_intersection_B(sectionName, torusBool, tubeName)
    elif np.pi < angle < 3./2. * np.pi:
        intersection = 'intersect_'+coneName
        solid = A_intersection_B(intersection, torusBool, coneName)
        exportRotation(intersection, solid, [180, 0, 0])        
        A_intersection_B(sectionName, intersection, tubeName)
    elif angle == 3./2.*np.pi:
        solid = A_intersection_B(sectionName, torusBool, tubeName)
        exportPosition(sectionName, solid, [0, 0, height/2])
    elif 3./2*np.pi < angle < 2*np.pi:
        notCone = 'not'+coneName
        A_minus_B(notCone, torusBool, coneName)
        A_intersection_B(sectionName, notCone, tubeName)
    elif angle == 2*np.pi:
        return None

    return sectionName


def processGDMLTorus(args):
    global lineNumber
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    torusName = "Torus_{}".format(lineNumber)

    rtor = args[0]  # distance from axis of torus to center of circle forming torus
    rin = rmin = args[1]  # radius of inside of torus (Rin in GPT parlance)
    rmax = rmin + defaultThickness
    a1 = args[2]  # these are in radians
    a2 = args[3]
    a1 = snapToQuadrant(a1)
    a2 = snapToQuadrant(a2)

    if a1 == 0 and a2 == 2*np.pi:
        ET.SubElement(solids, 'torus', {'name': torusName,
                                        'rmin': str(rmin),
                                        'rmax': str(rmax),
                                        'rtor': str(rtor),
                                        'startphi': '0',
                                        'deltaphi': '360',
                                        'aunit': 'deg',
                                        'lunit': 'mm'})
        return torusName

    # difficult case of torus cut by angles. Need to cut the torus
    # 1. Form a section from a1 to 2pi to represent permissible part starting from a1
    # 2. Form a section from a2 to 2pi.
    # 3. Form a section from 0 to a2, by subtracting section built in 2 from torus
    # 4. form the INTERSECTION of the first solid with the 3rd
    #
    solid1Name = torusSection(torusName+'_a1', a1, rin, rtor)  # a1 to 2pi
    solid2Name = torusSection(torusName+'_a2', a2, rin, rtor)  # a2 to 2pi
    # form 0 to a2 as full torus - a2 to 2p torus
    if solid2Name is None:  # no a2 to 2pi, so 0 to a2 is simply all of torus
        solid3Name = torusName+'_a2'
        torus(solid3Name, rin, rtor)
    else:
        solidName = 'not'+solid2Name
        torus(solidName, rin, rtor)
        solid3Name = solid1Name+'_minus_'+solid2Name
        A_minus_B(solid3Name, solidName, solid2Name)

    A_intersection_B(torusName, solid1Name, solid3Name)

    return torusName


def processGDMLSphere(args):
    global lineNumber
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    sphereName = "Sphere_{}".format(lineNumber)
    rmin = args[0]
    rmax = rmin + defaultThickness
    starttheta = np.degrees(args[1])
    deltatheta = np.degrees(args[2])
    startphi = 0
    deltaphi = 360
    ET.SubElement(solids, 'sphere', {'name': sphereName,
                                     'rmin': str(rmin),
                                     'rmax': str(rmax),
                                     'starttheta': str(starttheta),
                                     'deltatheta': str(deltatheta),
                                     'startphi': str(startphi),
                                     'deltaphi': str(deltaphi),
                                     'aunit': "deg",
                                     'lunit': 'mm'})

    return(sphereName)


def processGDMLCylinder(args):
    global lineNumber
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    cylName = "Tube_{}".format(lineNumber)
    rmin = args[0]
    height = args[1]
    rmax = rmin + defaultThickness
    startphi = 0
    deltaphi = 360
    ET.SubElement(solids, 'tube', {'name': cylName,
                                   'rmin': str(rmin),
                                   'rmax': str(rmax),
                                   'startphi': str(startphi),
                                   'deltaphi': str(deltaphi),
                                   'aunit': "deg",
                                   'z': str(height),
                                   'lunit': 'mm'})

    return(cylName)


def processGDMLBox(args):
    global lineNumber
    # Needs unique Name
    # flag needed for boolean otherwise parse twice
    boxName = "Box_{}".format(lineNumber)
    x = args[0]
    y = args[1]
    z = args[2]
    ET.SubElement(solids, 'box', {'name': boxName,
                                  'x': str(x),
                                  'y': str(y),
                                  'z': str(z),
                                  'lunit': 'mm'})

    return(boxName)


def createLVandPV(name, solidName, posRef, rotRef, matRef):
    global lineNumber
    global worldVOL
    #
    # Logical & Physical Volumes get added to structure section of gdml
    #
    # Need to update so that use export of Rotation & position
    # rather than this as well i.e one Place
    #
    # ET.ElementTree(gdml).write("test9d", 'utf-8', True)
    # print("Object Base")
    # dir(obj.Base)
    # print dir(obj)
    # print dir(obj.Placement)
    global PVcount
    global color_index
    # return
    pvName = 'PV_' + name
    PVcount += 1
    lvol = ET.SubElement(structure, 'volume', {'name': pvName})
    ET.SubElement(lvol, 'materialref', {'ref': matRef})
    ET.SubElement(lvol, 'solidref', {'ref': solidName})
    ET.SubElement(lvol, 'auxiliary', {'auxtype': "Color", 'auxvalue': colors[color_index]})
    color_index += 1
    color_index %= len(colors)

    # Place child physical volume in World Volume

    physVols.append([pvName, posRef, rotRef])


def processScatterLine(line):
    # get arguments
    func = line.split("(")
    solid = func[0][7:]
    args = func[1].split(")")

    if solid == 'cone':
        # for cone and tube location could is embedded in
        # in the arguments, as well
        # so we need a specialized ECS extractor
        d = getConeECSandArgs(args[0])
        solidName = processGDMLCone(d['args'])
        createLVandPV(solidName, solidName, d['posRef'], d['rotRef'], defaultMaterial)

    elif solid == 'pipe':
        # for cone and tube location could is embedded in
        # in the arguments, as well
        # so we need a specialized ECS extractor
        d = getPipeECSandArgs(args[0])
        solidName = processGDMLCylinder(d['args'])
        createLVandPV(solidName, solidName, d['posRef'], d['rotRef'], defaultMaterial)

    elif solid == 'iris':
        # process iris as cylinder with z = irisThickness
        d = getECSandArgs(args[0], defaultThickness/2)
        argList = d['args']
        r1 = float(argList[0])*1000
        r2 = float(argList[1])*1000
        height = defaultThickness
        solidName = processIRIS([r1, r2, height])
        createLVandPV(solidName, solidName, d['posRef'], d['rotRef'], defaultMaterial)

    elif solid == 'plate':
        d = getECSandArgs(args[0], defaultThickness/2)
        argList = d['args']
        x = float(argList[0])*1000
        y = float(argList[1])*1000
        z = defaultThickness
        solidName = processGDMLBox([x, y, z])
        createLVandPV(solidName, solidName, d['posRef'], d['rotRef'], defaultMaterial)

    elif solid == 'sphere':
        d = getECSandArgs(args[0])
        argList = d['args']
        R = float(argList[0])*1000
        a1 = float(eval(argList[1]))
        a2 = float(eval(argList[2]))
        z = defaultThickness
        solidName = processGDMLSphere([R, a1, a2])
        createLVandPV(solidName, solidName, d['posRef'], d['rotRef'], defaultMaterial)

    elif solid == 'torus':
        d = getECSandArgs(args[0])
        argList = d['args']
        Rout = float(argList[0])*1000
        Rin = float(argList[1])*1000
        if len(argList) > 2:
            a1 = float(eval(argList[2]))
            a2 = float(eval(argList[3]))
        else:
            a1 = 0
            a2 = 2*math.pi

        z = defaultThickness
        if a2 <= a1 or a1 < 0 or a2 < 0:
            print(f'******** Torus at {lineNumber}: a1, a2 not in range 0-2Pi or a1 >= a2')
        else:
            solidName = processGDMLTorus([Rout, Rin, a1, a2])
            createLVandPV(solidName, solidName, d['posRef'], d['rotRef'], defaultMaterial)


def processPseudoinfo(line):
    global defaultThickness, defaultMaterial
    # read parameters in commend line.
    # Follwing are parameters that will be processed:
    # thickness=xxx (xxx = thickness to be applied to next element, in mm)
    # material=G4_material, or STAINLEASS-STEEL
    irest = line.find("{")
    if irest == -1:
        return
    line = line[irest:]
    # workd online, but not here
    # pat = re.compile("^{[ ]*(\'material\':[ ]*\'G4_[-a-zA-Z]*\'[ ]*[,}])|(\'thickness\':[ ]*\'.*\'[ ]*[,}])")
    pat1 = re.compile("^{.*\'material\':[ ]*\'G4_[-a-zA-Z]*\'[ ]*[,}]")
    pat2 = re.compile("^{.*\'thickness\':[ ]*\'.*\'[ ]*[,}]")

    if pat1.match(line):
        parseDict = eval(line)
        if 'material' in parseDict:
            defaultMaterial = parseDict['material']

    if pat2.match(line):
        parseDict = eval(line)
        if 'thickness' in parseDict:
            defaultThickness = float(parseDict['thickness'])


def processFile(fileName):
    global lineNumber
    import logging
    logging.basicConfig(
        level=logging.INFO,
        filename="parselog.txt"
    )

    fd = open(fileName, 'r')

    for line in fd.readlines():
        line = line.strip()
        print(str(lineNumber)+' '+line)
        if len(line) > 0:
            yacc.parse(line, debug=logging.getLogger())
        lineNumber += 1

    fd.close()


def initGDML():
    NS = 'http://www.w3.org/2001/XMLSchema-instance'
    location_attribute = '{%s}noNamespaceSchemaLocation' % NS
    gdml = ET.Element('gdml', attrib={location_attribute:
                                      'http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd'})
    # print(gdml.tag)

          # 'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
          # 'xsi:noNamespaceSchemaLocation': "http://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd"
#})
    return gdml


def defineWorldBox(bbox):
    global solids
    name = 'WorldBox'
    ET.SubElement(solids, 'box', {'name': name,
                                  'x': str(10000),
                                  'y': str(10000),
                                  'z': str(10000),
                                  'lunit': 'mm'})
    return(name)


def createWorldVol(volName):
    print("Need to create Dummy Volume and World Box ")
    # TODO: At some point need to scan gpt .in file to determine bounding box
    bbox = [0, 0, 0, 10000, 10000, 10000]
    boxName = defineWorldBox(bbox)
    worldVol = ET.SubElement(structure, 'volume', {'name': volName})
    ET.SubElement(worldVol, 'solidref', {'ref': boxName})
    print("Need to FIX !!!! To use defined gas")
    ET.SubElement(worldVol, 'materialref', {'ref': 'G4_Galactic'})
    for physvol in physVols:
        phys = ET.SubElement(worldVol, 'physvol')
        ET.SubElement(phys, 'volumeref', {'ref': physvol[0]})
        ET.SubElement(phys, 'positionref', {'ref': physvol[1]})
        ET.SubElement(phys, 'rotationref', {'ref': physvol[2]})

    ET.SubElement(setup, 'world', {'ref': volName})
    return worldVol


physVols = []

GDMLstructure()
processFile(filename)
worldVOL = createWorldVol("World")
exportGDML(outFile)
