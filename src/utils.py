def year_to_num(s):
    """
    Convert a string made of numbers into a year
    Return 0 if string s is not a year, else return the year on 4 digits. ex: "73"-->1973
    """
    if isinstance(s, int):
        return s
    res = 0
    if str.isdigit(s):
        if len(s) == 4:
            res = int(s)
        else:
            if len(s) == 2:
                res = int("19" + s)
            # If year is 69 it means 1969.
            # Sounds ridiculous to have 16 instead of 2016.
    return res


def is_year(s):
    return s.isdigit() and (len(s) in (4, 2))


def capitalise_word(word):
    res = ""
    for i, l in enumerate(word):
        if i == 0:
            res += l.upper()
        else:
            res += l
    return res
