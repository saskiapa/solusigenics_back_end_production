import video


def get_video_by_disease(query):
    videos = video.Video.get_video_by_disease(query)  # Mendapatkan video-video dalam bentuk objek
    videos = video.convert_objects_to_dict(videos)  # Mengonversi objek ke dictionary
    video_ids = video.get_id_from_dicts(videos)
    videos_detail = video.get_video_detail_by_ids(query, video_ids)
    return {"videos": videos_detail}


def search(disease, query):
    videos_id = video.search(disease, query)
    videos_detail = video.get_video_detail_by_ids(disease, videos_id)
    return { "videos": videos_detail}


def get_play_url_by_id(id, source):
    return video.get_play_url_by_id(id, source)


def get_videos_detail(body):
    return {"videos": video.get_videos_detail(body)}


def get_video_recommendation(body):
    video_recommendations = video.get_video_recommendation(body)
    return {"videos": video_recommendations}
