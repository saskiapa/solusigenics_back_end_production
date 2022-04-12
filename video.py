import json
import random
import response
import disease_ignore
import pandas as pd
import math
import values

from os.path import exists as is_file_exist


class Video:
    def __init__(self, id, title, thumbnail, description):
        self.id = id
        self.title = title
        self.thumbnail = thumbnail
        self.description = description

    @staticmethod
    def get_yt_videos(q):
        # method ini digunakan untuk mengambil video dari API YouTube berdasarkan query

        videos = []  # list video
        ignored_video_id = disease_ignore.get_ignored_yt_videos()  # id-id video yang tidak akan ditampilkan

        i = 1
        while is_file_exist(f'./res/json_videos/{q}/YouTube/{i}.json'):  # cek keberadaan file
            with open(f'./res/json_videos/{q}/YouTube/{i}.json', encoding="utf8") as json_file:
                yt_response = json.load(json_file)
                yt_response = json.dumps(yt_response)
                yt_response = response.YouTubeResponse(yt_response)
                videos = videos + yt_response.get_video_list()
            i = i + 1

        videos = list(filter(lambda video: video["id"] not in ignored_video_id, videos))
        videos = convert_video_dict_to_object(videos)
        return videos

    @staticmethod
    def get_vm_videos(query):
        # method ini digunakan untuk mengambil video dari API Vimeo berdasarkan query

        videos = []
        ignored_video_id = disease_ignore.get_ignored_vimeo_videos()  # id-id video yang tidak akan ditampilkan

        i = 1
        while is_file_exist(f'./res/json_videos/{query}/Vimeo/{i}.json'):  # cek keberadaan file
            with open(f'./res/json_videos/{query}/Vimeo/{i}.json', encoding="utf8") as json_file:
                vm_response = json.load(json_file)
                vm_response = json.dumps(vm_response)
                vm_response = response.VimeoResponse(vm_response)
                videos = videos + vm_response.get_video_list()
            i = i + 1

        videos = list(filter(lambda video: video["id"] not in ignored_video_id, videos))
        videos = convert_video_dict_to_object(videos)
        return videos

    @staticmethod
    def get_all_yt_videos():
        videos = []
        diseases = [
            "Tipes",
            "Covid",
            "Diare",
            "Usus Buntu",
            "Diabetes",
            "TBC",
            "Hipertensi",
            "Demam Berdarah",
        ]
        for disease in diseases:
            videos = videos + Video.get_yt_videos(disease)
        return videos

    @staticmethod
    def get_all_vm_videos():
        videos = []
        diseases = [
            "Covid",
            "Demam Berdarah",
            "Diabetes",
            "Diare",
            "Hipertensi",
            "TBC",
            "Tipes",
            "Usus Buntu"
        ]
        for disease in diseases:
            videos = videos + Video.get_vm_videos(disease)
        return videos

    @staticmethod
    def get_video_by_disease(query):
        # method ini digunakan untuk mendapatkan video dari YouTube dan Vimeo

        # Mendapatkan video dari YouTube
        yt_videos = Video.get_yt_videos(query)

        # Mendapatkan video dari Vimeo
        vm_videos = Video.get_vm_videos(query)

        videos = yt_videos + vm_videos  # Menggabungkan video YouTube dan Vimeo
        videos = random.sample(videos, len(videos))  # Mengacak video
        return videos


class YouTubeVideo(Video):
    def __init__(self, id, title, thumbnail, description):
        Video.__init__(self, id, title, thumbnail, description)


class VimeoVideo(Video):
    def __init__(self, id, title, thumbnail, play_url, description):
        Video.__init__(self, id, title, thumbnail, description)
        self.play_url = play_url


def convert_video_dict_to_object(dicts):
    objects = []
    for dict in dicts:
        if dict["source"] == "YouTube":
            objects.append(YouTubeVideo(dict["id"], dict["title"], dict["thumbnail"], dict["description"]))
        else:
            objects.append(VimeoVideo(dict["id"], dict["title"], dict["thumbnail"], dict["embed"], dict["description"]))
    return objects


def convert_objects_to_dict(objects):
    dicts = []
    for o in objects:
        if isinstance(o, YouTubeVideo):
            dicts.append({
                "id": o.id,
                "title": o.title,
                "thumbnail": o.thumbnail,
                "source": "YouTube",
                "description": o.description,
            })
        else:
            dicts.append({
                "id": o.id,
                "title": o.title,
                "thumbnail": o.thumbnail,
                "playurl": o.play_url,
                "source": "Vimeo",
                "description": o.description,
            })
    return dicts


def get_number_of_document(corpuses):
    return len(corpuses)


def get_number_of_document_with_term(df, term):
    count = 0
    for i in range(0, len(df)):
        words = df.iloc[i]["title"].split(" ")
        words = list(filter(lambda word: word != "", words))
        if term in words:
            count = count + 1
    return count


def convert_kata_imbuhan_to_kata_dasar(word):
    with open("./res/kata_imbuhan_dan_dasarnya.json", "r") as json_file:
        data = json.load(json_file)
        keys = data.keys()
        if word in keys:
            return data[word]
    return word


def search(disease, term):
    term = term.lower()
    term = convert_kata_imbuhan_to_kata_dasar(term)
    df = pd.read_csv("./res/preprocessed_for_tf_idf/"+disease+".csv", sep="`")

    idf = 0
    if get_number_of_document_with_term(df, term) != 0:
        idf = math.log10(get_number_of_document(df) / get_number_of_document_with_term(df, term))

    tf_idfs = []
    for i in range(0, len(df)):
        document = df.iloc[i]["document"]
        words = document.split(" ")
        words = list(filter(lambda word: word != "", words))
        tf = words.count(term) / len(words)
        tf_idfs.append(tf * idf)

    df["tf_idf"] = tf_idfs

    df = df[df["tf_idf"] != 0.0]
    df = df.sort_values(by='tf_idf', ascending=False)

    video_ids = []
    for i in range(0, len(df)):
        video_ids.append(df.iloc[i]["id"])
    return video_ids


def search_multiple_term(disease, term, prev_video_id):
    term = term.lower()
    term = convert_kata_imbuhan_to_kata_dasar(term)
    df = pd.read_csv("./res/preprocessed_for_tf_idf/"+disease+".csv", sep="`")
    if (prev_video_id is not None) and (len(prev_video_id) != 0):
        df = df[df["id"].isin(prev_video_id)]

    idf = 0
    if get_number_of_document_with_term(df, term) != 0:
        idf = math.log10(get_number_of_document(df) / get_number_of_document_with_term(df, term))

    tf_idfs = []
    for i in range(0, len(df)):
        document = df.iloc[i]["document"]
        words = document.split(" ")
        words = list(filter(lambda word: word != "", words))
        tf = words.count(term) / len(words)
        tf_idfs.append(tf * idf)

    df["tf_idf"] = tf_idfs

    df = df[df["tf_idf"] != 0.0]
    df = df.sort_values(by='tf_idf', ascending=False)

    video_ids = []
    for i in range(0, len(df)):
        video_ids.append(df.iloc[i]["id"])
    if len(video_ids) == 0: # Jika tidak ada rekomendasi yang sesuai
        return prev_video_id
    return video_ids


def get_video_detail_by_ids(disease, ids):
    videos = Video.get_video_by_disease(disease)
    videos = convert_objects_to_dict(videos)
    videos = list(filter(lambda video: video["id"] in ids, videos))
    return videos


def get_id_from_dicts(dicts):
    ids = []
    for dict in dicts:
        ids.append(dict["id"])
    return ids


def get_play_url_by_id(id, source):
    if source == "YouTube":
        return f'https://www.youtube.com/embed/{id}'
    videos = Video.get_all_vm_videos()
    videos = convert_objects_to_dict(videos)
    videos = list(filter(lambda video: video["id"] == id, videos))
    video = videos[0]
    play_url = video["playurl"]
    play_url = play_url[13:]
    play_url = play_url[:play_url.index('"')]
    return play_url


def get_description_by_id(id, source):
    videos = None
    if source == "YouTube":
        videos = Video.get_all_yt_videos()
    else:
        videos = Video.get_all_vm_videos()
    videos = convert_objects_to_dict(videos)
    videos = list(filter(lambda video: video["id"] == id, videos))
    video = videos[0]
    description = video["description"]
    return description


def get_disease_by_id(id, source):
    diseases = [
        "Tipes",
        "Covid",
        "Diare",
        "Usus Buntu",
        "Diabetes",
        "TBC",
        "Hipertensi",
        "Demam Berdarah",
    ]
    if source == "YouTube":
        for disease in diseases:
            videos = Video.get_yt_videos(disease)
            videos = convert_objects_to_dict(videos)
            videos = list(filter(lambda video: video["id"] == id, videos))
            if len(videos) > 0:
                return disease
    for disease in diseases:
        videos = Video.get_vm_videos(disease)
        videos = convert_objects_to_dict(videos)
        videos = list(filter(lambda video: video["id"] == id, videos))
        if len(videos) > 0:
            return disease


def get_videos_detail(videos):
    df = pd.read_csv("./res/preprocessed_for_history_and_favorite/preprocessed_for_history_and_favorite_3.csv", sep="`")

    details = []
    for video in videos:
        row = df[(df.id == video["id"]) & (df.source == video["source"])].iloc[0]
        document = row.title + " " + (row.description if str(row.description) != "nan" else "")
        detail = {
            "id": row.id,
            "title": row.title,
            "thumbnail": row.thumbnail,
            "source": row.source,
            "disease": row.disease,
            "document": document
        }
        details.append(detail)
        # print("\n", detail)
    return details


def get_video_keyword():
    keywords = pd.read_excel('./res/Keywords.xlsx', header=None)
    return keywords[0].tolist()


def join_videos_document_and_process_for_video_recommendation(videos):
    keywords = get_video_keyword()

    punctuations = values.punctuations
    emoticons = values.emoticons
    special_characters = values.special_characters

    documents = " "
    for video in videos:
        documents = documents + " " + video["document"]
    documents = documents.strip()

    for punctuation in punctuations:
        documents = documents.replace(punctuation, " ")

    for emot in emoticons:
        documents = documents.replace(emot, " ")

    for i in range(0, 10):
        documents = documents.replace(str(i), " ")

    document_word = documents.split(" ")
    document_word = list(filter(lambda title: title not in special_characters, document_word))

    i = 0
    while i < len(document_word):
        document_word[i] = document_word[i].lower()
        i = i + 1

    document_word = list(filter(lambda word: word != '', document_word))
    document_word = list(filter(lambda word: word != ' ', document_word))

    document_word = list(filter(lambda word: word in keywords, document_word))

    return document_word


def get_video_recommendation_ids(videos):
    # Memisahkan video-video berdasarkan penyakit
    tipes_videos = list(filter(lambda video: video["disease"] == 'Tipes', videos))
    covid_videos = list(filter(lambda video: video["disease"] == 'Covid', videos))
    diare_videos = list(filter(lambda video: video["disease"] == 'Diare', videos))
    ub_videos = list(filter(lambda video: video["disease"] == 'Usus Buntu', videos))
    diabetes_videos = list(filter(lambda video: video["disease"] == 'Diabetes', videos))
    tbc_videos = list(filter(lambda video: video["disease"] == 'TBC', videos))
    hipertensi_videos = list(filter(lambda video: video["disease"] == 'Hipertensi', videos))
    dbd_videos = list(filter(lambda video: video["disease"] == 'Demam Berdarah', videos))

    # Mendapatkan keyword berdasarkan title video
    tipes_keyword = join_videos_document_and_process_for_video_recommendation(tipes_videos)
    covid_keyword = join_videos_document_and_process_for_video_recommendation(covid_videos)
    diare_keyword = join_videos_document_and_process_for_video_recommendation(diare_videos)
    ub_keyword = join_videos_document_and_process_for_video_recommendation(ub_videos)
    diabetes_keyword = join_videos_document_and_process_for_video_recommendation(diabetes_videos)
    tbc_keyword = join_videos_document_and_process_for_video_recommendation(tbc_videos)
    hipertensi_keyword = join_videos_document_and_process_for_video_recommendation(hipertensi_videos)
    dbd_keyword = join_videos_document_and_process_for_video_recommendation(dbd_videos)

    # Menghapus keyword yang duplikat
    tipes_keyword = list(set(tipes_keyword))
    covid_keyword = list(set(covid_keyword))
    diare_keyword = list(set(diare_keyword))
    ub_keyword = list(set(ub_keyword))
    diabetes_keyword = list(set(diabetes_keyword))
    tbc_keyword = list(set(tbc_keyword))
    hipertensi_keyword = list(set(hipertensi_keyword))
    dbd_keyword = list(set(dbd_keyword))

    # Mendapatkan rekomendasi video berdasarkan keyword dan penyakitnya
    tipes_recommendation = []
    for keyword in tipes_keyword:
        tipes_recommendation = tipes_recommendation + search("Tipes", keyword)

    covid_recommendation = []
    for keyword in covid_keyword:
        covid_recommendation = covid_recommendation + search("Covid", keyword)

    diare_recommendation = []
    for keyword in diare_keyword:
        diare_recommendation = diare_recommendation + search("Diare", keyword)

    ub_recommendation = []
    for keyword in ub_keyword:
        ub_recommendation = ub_recommendation + search("Usus Buntu", keyword)

    diabetes_recommendation = []
    for keyword in diabetes_keyword:
        diabetes_recommendation = diabetes_recommendation + search("Diabetes", keyword)

    tbc_recommendation = []
    for keyword in tbc_keyword:
        tbc_recommendation = tbc_recommendation + search("TBC", keyword)

    hipertensi_recommendation = []
    for keyword in hipertensi_keyword:
        hipertensi_recommendation = hipertensi_recommendation + search("Hipertensi", keyword)

    dbd_recommendation = []
    for keyword in dbd_keyword:
        dbd_recommendation = dbd_recommendation + search("Demam Berdarah", keyword)

    # Menggabungkan semua rekomendasi video
    video_recommendation_ids = tipes_recommendation
    video_recommendation_ids = video_recommendation_ids + covid_recommendation
    video_recommendation_ids = video_recommendation_ids + diare_recommendation
    video_recommendation_ids = video_recommendation_ids + ub_recommendation
    video_recommendation_ids = video_recommendation_ids + diabetes_recommendation
    video_recommendation_ids = video_recommendation_ids + tbc_recommendation
    video_recommendation_ids = video_recommendation_ids + hipertensi_recommendation
    video_recommendation_ids = video_recommendation_ids + dbd_recommendation

    # Megnhapus id video yang duplikat
    video_recommendation_ids = list(set(video_recommendation_ids))
    return video_recommendation_ids


def get_cosine_similarity(text1, text2):
    list_word_text_1 = text1.split(" ")
    list_word_text_2 = text2.split(" ")

    all_word = set(list_word_text_1).union(set(list_word_text_2))
    all_word = list(all_word)

    df = pd.DataFrame(columns= all_word)
    for word in all_word:
        column_value = []
        column_value.append(list_word_text_1.count(word))
        column_value.append(list_word_text_2.count(word))
        df[word] = column_value

    pembilang = 0
    for word in all_word:
        pembilang = pembilang + df.iat[0, df.columns.get_loc(word)] * df.iat[1, df.columns.get_loc(word)]

    penyebut = math.sqrt(sum(map(lambda x:x*x,df.loc[0]))) * math.sqrt(sum(map(lambda x:x*x,df.loc[1])))
    cosine_similarity = pembilang / penyebut
    return cosine_similarity


def get_similarity_per_disease(video_favorite, video_recommendation):
    cols = ["id", "similarity"]
    df = pd.DataFrame(columns=cols)

    if len(video_favorite) != 0 and len(video_recommendation) != 0:
        for v1 in video_favorite:
            for v2 in video_recommendation:
                df_append = pd.DataFrame([[v2["id"], get_cosine_similarity(v1["title"], v2["title"])]], columns=cols)
                df = pd.concat([df, df_append])
    return df


def sort_by_similarity(
    video_favorite_tipes,
    video_favorite_covid,
    video_favorite_diare,
    video_favorite_ub,
    video_favorite_diabetes,
    video_favorite_tbc,
    video_favorite_hipertensi,
    video_favorite_dbd,
    video_tipes,
    video_covid,
    video_diare,
    video_ub,
    video_diabetes,
    video_tbc,
    video_hipertensi,
    video_dbd
    ):
    cols = ["id", "similarity"]
    df = pd.DataFrame(columns=cols)

    df_tipes = get_similarity_per_disease(video_favorite_tipes, video_tipes)
    df = pd.concat([df, df_tipes], ignore_index=True)

    df_covid = get_similarity_per_disease(video_favorite_covid, video_covid)
    df = pd.concat([df, df_covid], ignore_index=True)

    df_diare = get_similarity_per_disease(video_favorite_diare, video_diare)
    df = pd.concat([df, df_diare], ignore_index=True)

    df_ub = get_similarity_per_disease(video_favorite_ub, video_ub)
    df = pd.concat([df, df_ub], ignore_index=True)

    df_diabetes = get_similarity_per_disease(video_favorite_diabetes, video_diabetes)
    df = pd.concat([df, df_diabetes], ignore_index=True)

    df_tbc = get_similarity_per_disease(video_favorite_tbc, video_tbc)
    df = pd.concat([df, df_tbc], ignore_index=True)

    df_hipertensi = get_similarity_per_disease(video_favorite_hipertensi, video_hipertensi)
    df = pd.concat([df, df_hipertensi], ignore_index=True)

    df_dbd = get_similarity_per_disease(video_favorite_dbd, video_dbd)
    df = pd.concat([df, df_dbd], ignore_index=True)

    df = df.sort_values(by="similarity", ascending=False)
    df = df.drop_duplicates(subset=['id'])
    video_recommendation_ids = df["id"]
    video_recommendation_ids = list(video_recommendation_ids)
    return video_recommendation_ids


def get_video_recommendation(videos):
    videos = get_videos_detail(videos)

    video_favorite_tipes = []
    video_favorite_covid = []
    video_favorite_diare = []
    video_favorite_ub = []
    video_favorite_diabetes = []
    video_favorite_tbc = []
    video_favorite_hipertensi = []
    video_favorite_dbd = []

    for v in videos:
        if v["disease"] == "Tipes":
            video_favorite_tipes.append(v)
        elif v["disease"] == "Covid":
            video_favorite_covid.append(v)
        elif v["disease"] == "Diare":
            video_favorite_diare.append(v)
        elif v["disease"] == "Usus Buntu":
            video_favorite_ub.append(v)
        elif v["disease"] == "Diabetes":
            video_favorite_diabetes.append(v)
        elif v["disease"] == "TBC":
            video_favorite_tbc.append(v)
        elif v["disease"] == "Hipertensi":
            video_favorite_hipertensi.append(v)
        elif v["disease"] == "Demam Berdarah":
            video_favorite_dbd.append(v)

    curr_video_id = []

    for video in videos:
        curr_video_id.append(video["id"])
        del video["id"]
        del video["thumbnail"]
        del video["source"]

    video_recommendation_ids = get_video_recommendation_ids(videos)
    video_recommendation_ids = list(filter(lambda id: id not in curr_video_id, video_recommendation_ids))
    videos_detail = []

    for id in video_recommendation_ids:
        video_disease = get_video_disease(id)
        video_detail = get_video_detail_by_ids(
            video_disease,
            [id]
        )
        video_detail[0]["disease"] = video_disease
        videos_detail.append(video_detail[0])
    video_tipes = []
    video_covid = []
    video_diare = []
    video_ub = []
    video_diabetes = []
    video_tbc = []
    video_hipertensi = []
    video_dbd = []
    for vd in videos_detail:
        if vd["disease"] == "Tipes":
            video_tipes.append(vd)
        elif vd["disease"] == "Covid":
            video_covid.append(vd)
        elif vd["disease"] == "Diare":
            video_diare.append(vd)
        elif vd["disease"] == "Usus Buntu":
            video_ub.append(vd)
        elif vd["disease"] == "Diabetes":
            video_diabetes.append(vd)
        elif vd["disease"] == "TBC":
            video_tbc.append(vd)
        elif vd["disease"] == "Hipertensi":
            video_hipertensi.append(vd)
        elif vd["disease"] == "Demam Berdarah":
            video_dbd.append(vd)

    video_recommendation_ids = sort_by_similarity(
        video_favorite_tipes,
        video_favorite_covid,
        video_favorite_diare,
        video_favorite_ub,
        video_favorite_diabetes,
        video_favorite_tbc,
        video_favorite_hipertensi,
        video_favorite_dbd,
        video_tipes,
        video_covid,
        video_diare,
        video_ub,
        video_diabetes,
        video_tbc,
        video_hipertensi,
        video_dbd
    )
    for id in video_recommendation_ids:
        video_disease = get_video_disease(id)
        video_detail = get_video_detail_by_ids(
            video_disease,
            [id]
        )
        video_detail[0]["disease"] = video_disease
        videos_detail.append(video_detail[0])

    return videos_detail


def get_video_disease(video_id):
    df = pd.read_csv("./res/preprocessed_for_history_and_favorite/preprocessed_for_history_and_favorite_2.csv", sep="`")
    df = df[df['id'] == video_id]
    disease = df.iloc[0]['disease']
    return disease
