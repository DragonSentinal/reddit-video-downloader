import requests
import bs4
import os


def download_file(link, name):
    request = requests.get(link)
    file = open(name, "wb")
    for chunk in request.iter_content(100000):
        file.write(chunk)
    file.close()


if __name__ == "__main__":
    print("gimme a reddit link with a video")
    reddit_link = input()

    reddit_page = requests.get(reddit_link)
    reddit_page.raise_for_status()

    # Craft the link to the DASH MPD
    content_id_soup = bs4.BeautifulSoup(reddit_page.text, "html.parser")
    content_id_element = content_id_soup.select("shreddit-post[post-type=\"video\"]")[0]  # Tag that I chose that has ID
    content_id_attribute = content_id_element.get("content-href")  # content-href attribute holds a link with the ID
    content_id = content_id_attribute[18:]
    data_mpd_link = f"https://v.redd.it/{content_id}/DASHPlaylist.mpd"

    data_mpd = requests.get(data_mpd_link)
    data_mpd.raise_for_status()

    # Craft the links to video and audio components
    data_mpd_soup = bs4.BeautifulSoup(data_mpd.text, "xml")  # Chuck MPD file into xml parser
    data_mpd_element = data_mpd_soup.findAll("BaseURL")  # BaseURL tag holds information to video and audio file
    video_element = data_mpd_element[len(data_mpd_element) - 2].getText()
    video_component_link = f"https://v.redd.it/{content_id}/{video_element}"  # Link to max quality video
    audio_element = data_mpd_element[len(data_mpd_element) - 1].getText()
    audio_component_link = f"https://v.redd.it/{content_id}/{audio_element}"

    post_name = content_id_element.get("post-title")  # Grab title of the post to name output
    video_component_name = f"videoComponent - {post_name}.mp4"
    audio_component_name = f"audioComponent - {post_name}.mp4"
    result_name = f"{post_name}.mp4"

    print("Downloading video component")
    download_file(video_component_link, video_component_name)
    print("Downloading audio component")
    download_file(audio_component_link, audio_component_name)

    print(f"ffmpeg -i \"{video_component_name}\" -i \"{audio_component_name}\" -c:v copy -c:a copy \"{result_name}\"")

    print("Attempting to smash them together with ffmpeg")
    os.system(
        f"ffmpeg -i \"{video_component_name}\" -i \"{audio_component_name}\" -c:v copy -c:a copy \"{result_name}\"")

    print("If ffmpeg is screaming errors it probably didn't work")

    print("Deleting component files")
    os.unlink(video_component_name)
    os.unlink(audio_component_name)

    print("Press Enter to exit")

    input()
