"""
Created on Sun Mar 29 02:50:34 2015

@author: DH
"""

# order of operations (functions need parentheses)
# note: for postscript, exp means power (exponent) -- not exp(x)
precedence = {"sin":0, "cos":0, "tan":0, "log":0, "ln":0, "sqrt":0, "abs":0,
              "exp":1, "mul":2, "div":2, "add":3, "sub":3}

# a list of all operations, and parentheses
all_ops = precedence.keys() + ["(", ")"]

binary_ops_math = ["**", "*", "/", "+", "-"]          # the binary operation names in math
binary_ops_rpn = ["exp", "mul", "div", "add", "sub"]  # the binary operation names PS uses

# some auxiliary functions

def padChar(op, char):
    return char + op + char

def flatten(L):
    ''' flatten a nested list '''
    if L == []:
        return L
    if isinstance(L[0], list):
        return flatten(L[0]) + flatten(L[1:])
    return L[:1] + flatten(L[1:])

def checkParentheses(expr):
    ''' check that all parentheses match up correctly '''
    sum = 0
    for char in expr:
        if char == "(":
            sum += 1
        if char == ")":
            sum -= 1
        if sum < 0:    #"There's a ')' without an opening '('"
            return 0 
    if sum > 0:        #"There's a '(' without a closing ')'"
        return 0 
    if sum == 0:
        return 1

def replaceSubWithNegativeOne(expr_list):
    ''' if sub has an operator or '(' on its left, we'll change it to [-1, mul] and flatten
    '''
    expr = [i for i in expr_list]
    ind = 0
    for element in expr:
        replacement = ["-1", "mul"]
        if element == "sub":
            if ind == 0:
                expr[ind] = replacement
            elif expr[ind - 1] in all_ops[:-1]:
                expr[ind] = replacement
        ind += 1
    return flatten(expr)

def exprToList(expression):
    ''' input an expression, output list of #'s/variables/operations 
    (expression can use either '^' or '**' for exponentiation)'''
    
    expr = expression
    expr = expr.replace("^", "**")     # since we can also have "^" mean exponentiation

    # replace {**, *, /, +, -} with {exp, mul, div, add, sub}
    for op_math, op_rpn in zip(binary_ops_math, binary_ops_rpn):
        expr = expr.replace(op_math, padChar(op_rpn," "))
        
    # add commas before/after all operators and parentheses
    for op in all_ops:
        expr = expr.replace(op, padChar(op, ","))
    
    expr = expr.replace(" ","")        # we don't want spaces in the list
        
    # need to remove empty strings from the list
    expr = filter(None, expr.split(","))
    
    # allow negative numbers 
    expr = replaceSubWithNegativeOne(expr)
    
    return expr
    
def binaryRPN(expr, ind):
    ''' turn [... , l_(i-1), l_i, l_(i+1), ...] into 
    [... ,[l_(i-1), l_(i+1), l_i], ...] '''
    expr[ind] = [expr[ind - 1], expr[ind + 1], expr[ind]]
    del expr[ind + 1]
    del expr[ind - 1]
    
def unaryRPN(expr, ind):
    ''' turn [... , l_i, l_(i+1), ...] into [... ,[l_(i+1), l_i], ...]  '''
    expr[ind] = [expr[ind + 1], expr[ind]]
    del expr[ind + 1]
    
def findClosingParen(expr_list, ind):
    ''' given list expr_list and index ind of a '(',
    returns index of closing ')'
    '''
    sum = 0
    i = ind
    for char in expr_list[ind:]:
        if char == "(":
            sum += 1
        if char == ")":
            sum -= 1
        if sum == 0:
            return i
        i += 1

def exprListToRPN(expr_list):
    ''' given input expression as a list,
    returns RPN-expression as a list
    '''
    expr = [i for i in expr_list]
    
    # take care of parentheses recursively
    ind = 0
    while ind < len(expr):
        element = expr[ind]
        if element == "(":
            ind_close = findClosingParen(expr, ind)
            expr[ind] = exprListToRPN(expr[ind + 1 : ind_close])
            del expr[ind + 1 : ind_close + 1]
        ind += 1
    
    # take care of binary/unary operations
    for prec in range(4):
        # ind keeps track of where we are in expr
        ind = 0
        while ind < len(expr):
            element = expr[ind]
            # if expr[ind] is an operator of precedence prec,
            # then nest down a level
            if element in precedence.keys():
                if precedence[element] == prec:
                    if prec == 0:
                        # deal with functions
                        unaryRPN(expr, ind)
                    else: 
                        # deal with binary op's
                        binaryRPN(expr, ind)
                        # we're putting expr[ind - 1] into the nested list,
                        # so we need to reduce ind by 1
                        ind -= 1
            ind += 1
            
    # at this point, expr is a nested list
    return flatten(expr)


def getRPN(expr):
    ''' convert expression into RPN
    (can use either "^" or "**" for exponentiation)
    
    Ex: convert "-sin(pi/4) + 3*abs(x+7) - x^.5" to
    '-1 pi 4 div sin mul 3 x 7 add abs mul add x .5 exp sub'
    '''
    
    # make sure that parentheses all match
    paren_check = checkParentheses(expr)
    if paren_check == 0:
        print "Parentheses don't match"
        return
    
    expr_list = exprToList(expr)
    expr_list_RPN = exprListToRPN(expr_list)
    output_RPN = " ".join(expr_list_RPN)
    
    return output_RPN
    
    
######################################################################
###########                SOME EXAMPLES           ###################
######################################################################

expr1 = "a*x^2+b*x+c"
print "\n", getRPN(expr1)

expr2 = "-3*2**(x+1)"
print "\n", getRPN(expr2)

expr3 = "-sin(pi/4) + 3*abs(x+7) - x^.5"
print "\n", getRPN(expr3)

expr4 = "(2/pi*e^(-x^2/10))*sin(-pi*x)"
print "\n", getRPN(expr4)

expr5 = "-.005*(x+10)^3*(x+1)*(x-4)^.5*(x-10)/(x^2+1)"
print "\n", getRPN(expr5)
