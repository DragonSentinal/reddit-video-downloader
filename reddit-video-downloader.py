import requests
import bs4
import os


def downloadFile(link, name):
    request = requests.get(link)
    file = open(name, "wb")
    for chunk in request.iter_content(100000):
        file.write(chunk)
    file.close()


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    print("gimme a reddit link with a video")
    redditLink = input()

    # request the reddit page
    redditPage = requests.get(redditLink)
    redditPage.raise_for_status()

    # craft the link to the DASH MPD
    contentIDSoup = bs4.BeautifulSoup(redditPage.text, "html.parser")  # chuck page into the parser
    contentIDElement = contentIDSoup.select("shreddit-post[post-type=\"video\"]")[0]  # find the tag
    contentIDAttribute = contentIDElement.get("content-href")  # grab the desired attribute
    contentID = contentIDAttribute[18:]  # slices the actual ID off the tail end of the link
    dataMPDLink = f"https://v.redd.it/{contentID}/DASHPlaylist.mpd"  # craft link to MPD file

    # request the DASH MPD
    dataMPD = requests.get(dataMPDLink)
    dataMPD.raise_for_status()

    dataMPDSoup = bs4.BeautifulSoup(dataMPD.text, "xml")  # chuck MPD file into xml parser
    dataMPDElement = dataMPDSoup.findAll("BaseURL")  # BaseURL tag holds information to video and audio file
    videoElement = dataMPDElement[len(dataMPDElement) - 2].getText()
    videoComponentLink = f"https://v.redd.it/{contentID}/{videoElement}"  # link to max quality video
    audioElement = dataMPDElement[len(dataMPDElement) - 1].getText()
    audioComponentLink = f"https://v.redd.it/{contentID}/{audioElement}"  # link to audio

    postName = contentIDElement.get("post-title")  # grab title of the post to name output
    videoComponentName = f"videoComponent - {postName}.mp4"
    audioComponentName = f"audioComponent - {postName}.mp4"
    resultName = f"{postName}.mp4"

    # download both components
    print("Downloading video component")
    downloadFile(videoComponentLink, videoComponentName)
    print("Downloading audio component")
    downloadFile(audioComponentLink, audioComponentName)

    print(f"ffmpeg -i \"{videoComponentName}\" -i \"{audioComponentName}\" -c:v copy -c:a copy \"{resultName}\"")

    print("Attempting to smash them together with ffmpeg")
    os.system(f"ffmpeg -i \"{videoComponentName}\" -i \"{audioComponentName}\" -c:v copy -c:a copy \"{resultName}\"")

    print("If ffmpeg is screaming errors it probably didn't work")

    print("Deleting component files")
    os.unlink(videoComponentName)
    os.unlink(audioComponentName)

    print("Press Enter to exit")

    input()
