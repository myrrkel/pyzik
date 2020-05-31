def keyToString(key):
    skey = ""
    for c in key:
        if c.isdigit():
            n = chr(97 + int(c))
            skey = skey + n.upper()
        else:
            skey = skey + c

    return skey


def stringToKey(s):
    """
    Please, get your own dev api key at https://dirble.com/users/sign_in
    """
    key = ""

    for c in s:
        if c == c.upper():
            n = ord(c.lower()) - 97
            key = key + str(n)
        else:
            key = key + c

    return key


def keyToString2(key):
    skey = ""
    chars = key.split("-")
    for char in chars:
        # print(char)
        skey = skey + chr(int(char))

    return skey


def stringToKey2(s):
    """
    Please, get your own dev api key at https://console.developers.google.com/apis
    """
    key = ""

    for c in s:
        n = ord(c)
        if key != "": key = key + '-'
        key = key + str(n)

    return key


dirbleAPIKey = stringToKey("HcFaFbIfICffGcffFGHGCCBddD")
darAPIKey = stringToKey("EDJFIIGAFA")
ytubeAPIKey = keyToString2(
    "65-73-122-97-83-121-67-83-57-56-121-119-72-111-118-101-83-98-109-109-115-107-82-51-50-97-68-65-120-117-73-100-97-121-78-108-95-98-89")
