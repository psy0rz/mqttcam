from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo

from log import log
def upload(file, title, description, tags, category, language, privacy_status):

    log("uploading...")

    # loggin into the channel
    channel = Channel()
    channel.login("youtube_client_secret.json", "youtube_credentials.storage")

    # setting up the video that is going to be uploaded
    video = LocalVideo(file_path=file)

    # setting snippet
    video.set_title(title)
    video.set_description(description)
    video.set_tags(tags)
    video.set_category(category)
    video.set_default_language(language)

    # setting status
    video.set_embeddable(True)
    video.set_license("creativeCommon")
    video.set_privacy_status(privacy_status)
    video.set_public_stats_viewable(True)

    # setting thumbnail
    # video.set_thumbnail_path('test_thumb.png')

    # uploading video and printing the results
    video = channel.upload_video(video)
    log(video.id)
    log(video)

    # liking video
    # video.like()
    log("upload complete`")
