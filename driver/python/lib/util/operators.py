
def optUtil(value):
    op = value&0xFFFF
    value>>=16
    value&=0xFFFF

    value|=(op<<16)

    #if (value&0x80000000):
    #    value|=0xFFFFFFFF00000000
    # Python 3 does not have a long type. Instead, int itself allows large values (limited only by available memory); in effect, Python 2’s long was renamed to int.
    # In Python it does not work. See https://portingguide.readthedocs.io/en/latest/numbers.html
    # Solution is below:

    if (value&0x80000000):
        value=not value
        value=-(value+1)

    return (int)(value)

def fixedPoint(value, size, precision):
    valueStr = ("{:0" + str(size) + "d}").format(value)
    i = len(valueStr) - precision
    return valueStr[:i] + "." + valueStr[i:]
