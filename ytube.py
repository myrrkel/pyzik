  

    r = requests.get("https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=25&q=power+of+zeus&key="+ytubeAPIKey)
    print(r.text)
