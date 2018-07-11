  

    r = requests.get("https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=25&q=power+of+zeus&key="+ytubeAPIKey)
    print(r.text)



# For lyrics: https://git.weboob.org/aerogus/devel/blob/master/modules/lyricsplanet/browser.py
# https://legacy-api.kexp.org/show/?format=json&limit=1
# https://legacy-api.kexp.org/play/?format=json&limit=1&ordering=-airdate
# https://www.franceinter.fr/programmes?xmlHttpRequest=1
# https://www.franceculture.fr/programmes?xmlHttpRequest=1