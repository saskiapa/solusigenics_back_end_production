import json


class Response:
    # Kelas ini digunakan sebagai blueprint hasil response

    def __init__(self, raw_response):
        self.raw_response = raw_response  # hasil respon


class YouTubeResponse(Response):
    def __init__(self, raw_response):
        super().__init__(raw_response)

        self.raw_response = json.loads(self.raw_response)  # mengubah hasil respon ke bentuk json
        self.items = []  # untuk menampung video-video

        # Mendapatkan id, thumbnail, dan title video
        for item in self.raw_response['items']:
            video_id = item["id"]["videoId"]
            thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
            title = item["snippet"]["title"]
            description = item["snippet"]["description"]
            video = {
                "id": video_id,
                "thumbnail": thumbnail,
                "title": title,
                "source": "YouTube",
                "description": description,
            }
            self.items.append(video)

    def get_video_list(self):
        return self.items


class VimeoResponse(Response):
    def __init__(self, raw_response):
        super().__init__(raw_response)

        self.raw_response = json.loads(self.raw_response)  # mengubah hasil respon ke bentuk json
        self.items = []  # untuk menampung video-video

        # Mendapatkan thumbnail, dan title dan embed video
        for item in self.raw_response['data']:
            video_id = item["uri"]
            video_id = video_id[8:]
            thumbnail = item["pictures"]["base_link"]
            title = item["name"]
            embed = item["embed"]["html"]
            description = item["description"]
            video = {
                "id": video_id,
                "thumbnail": thumbnail,
                "title": title,
                "embed": embed,
                "source": "Vimeo",
                "description": description,
            }
            self.items.append(video)

    def get_video_list(self):
        return self.items
