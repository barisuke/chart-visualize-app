import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder


#　各特徴量
class HakensakiHaizokuSakiBusho:
    """
    """
    def __init__(self):
        self.col_name = "（派遣先）配属先部署"
        with open(f'./module/encoders/{self.col_name}_encoder.pkl', 'rb') as f:
            self.encoder = pickle.load(f)
    def encode(self, series):
        return self.encoder.transform(series.fillna("MISSING"))


class KinmuchiMoyorieki1Ekimei:
    """
    """
    def __init__(self):
        self.col_name = "勤務地　最寄駅1（駅名）"
        with open(f'./module/encoders/{self.col_name}_encoder.pkl', 'rb') as f:
            self.encoder = pickle.load(f)

    def encode(self, series):
        return self.encoder.transform(series.fillna("MISSING"))


class KinmuchiMoyorieki1Ensenmei:
    """
    """
    def __init__(self):
        self.col_name = "勤務地　最寄駅1（沿線名）"
        with open(f'./module/encoders/{self.col_name}_encoder.pkl', 'rb') as f:
            self.encoder = pickle.load(f)

    def encode(self, series):
        return self.encoder.transform(series.fillna("MISSING"))


# 前処理本体
class DataProcessor:
    def __init__(self):        
        self.hhsb = HakensakiHaizokuSakiBusho()
        self.km1eki = KinmuchiMoyorieki1Ekimei()
        self.km1ensen = KinmuchiMoyorieki1Ensenmei()
    def format_x(self, X):
        try:
            X["（派遣先）配属先部署"] = self.hhsb.encode(X["（派遣先）配属先部署"])
        except Exception as e:
            print(e)
            print("（派遣先）配属先部署　に問題あり")
        try:
            X["勤務地　最寄駅1（駅名）"] = self.km1eki.encode(X["勤務地　最寄駅1（駅名）"])
        except Exception as e:
            print(e)
            print("勤務地　最寄駅1（駅名）　に問題あり")
        try:
            X["勤務地　最寄駅1（沿線名）"] = self.km1ensen.encode(X["勤務地　最寄駅1（沿線名）"])
        except Exception as e:
            print(e)
            print("勤務地　最寄駅1（沿線名） に問題あり")
        return X