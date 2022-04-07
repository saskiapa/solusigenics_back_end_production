import pandas as pd


def get_ignored_yt_videos():
    df = pd.read_excel("./res/disease_ignore.xlsx", header=None, sheet_name="YouTube")
    disease = list(df[0])
    return disease


def get_ignored_vimeo_videos():
    df = pd.read_excel("./res/disease_ignore.xlsx", header=None, sheet_name="Vimeo")
    df[0] = df[0].apply(lambda x: str(x)[0:len(str(x))-2])
    disease = list(df[0])
    return disease
