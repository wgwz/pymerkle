import math

# ------------------------------ Math utilities --------------------------


def log_2(length):
    """
    Logarithm with base 2

    :param length : <int>
    :returns      : <int>

    Returns the logarithm of the greatest power of 2 equal to or smaller than `length`

    NOTE: Throws

    ValueError: math domain IndexError

    for arguments smaller than zero.
    """
    return 0 if length == 0 else int(math.log(length, 2))


def powers_of(integer):
    """
    Additive decomposition in decreasing powers of 2

    :param integer : <int>
    :returns       : <list [of <int>]>

    NOTE: Returns the nonsensical empty list [] for any argument equal to
    or smaller than zero.
    """
    powers = []
    while integer > 0:
        power = log_2(integer)
        integer -= 2**power
        powers.append(power)
    return tuple(powers)

# ------------------------------ Format utilities------------------------------


def get_with_sign(num):
    """
    param num : <int>
    returns   : <str>
    """
    if num >= 0:
        sign = '+'
    else:
        sign = '-'
    return sign + str(abs(num))


def stringify_path(signed_hashes):
    """
    Returns a nice formatted stringified version of the inserted list of signed hashes
    (e.g., for the first outpout of the merkle_tree._audit_path() function)

    :param signed_hashes : <list [of (+1/-1, <str>)]> or None
    :returns             : <str>
    """
    def order_of_magnitude(num): return 0 if num == 0 else int(math.log10(num))

    if signed_hashes is not None:
        stringified_elems = []
        for i in range(len(signed_hashes)):
            elem = signed_hashes[i]
            stringified_elems.append(
                ('\n' +
                 (7 - order_of_magnitude(i)) *
                 ' ' +
                 '[{i}]' +
                 3 *
                 ' ' +
                 '{sign}' +
                 2 *
                 ' ' +
                 '{hash}').format(
                    i=i,
                    sign=get_with_sign(
                        elem[0]),
                    hash=elem[1]))
        return ''.join(elem for elem in stringified_elems)
    return ''  # input was None
