import os
import csv
import logging
from io import StringIO
from urllib.parse import quote

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, make_response
from google.cloud import bigquery
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
client = bigquery.Client()


@app.route('/')
def index():
    return render_template('csv.html', fig=None, alert="csvファイルを選択＆送信してください")


@app.route('/api', methods=["GET"])
def fetch_bigquery():
    query = """
    SELECT * FROM (
        SELECT * FROM `kernel-mlops.IMU.MbientlabSensor` ORDER BY time DESC LIMIT 10
    ) AS desc_table
    ORDER BY time;"""
    query_job = client.query(query)  # Make an API request.
    query = query_job.result()  # Waits for query to finish
    return query.to_dataframe().to_json()


@app.route('/download_csv', methods=['GET', 'POST'])
def download_csv():
    if request.method == 'POST':
        save_filename = ""
        filename_list = []
        send_data_list = request.files.getlist('send_data[]')
        app.logger.info(f'# of uploaded files: {len(send_data_list)}')

        try:
            all_df_list = []
            for send_data in send_data_list:
                filename_list.append(send_data.filename)
                app.logger.info(f'Uploaded: {send_data}')
                dfs = pd.read_csv(
                    send_data, encoding="shift-jis", chunksize=5000)
                for df in dfs:
                    predicted = model_api.predict(df)
                    df["ai_score"] = predicted
                    all_df_list.append(df)

            # NOTE: copy=False: この後に元のdataframeが必要ない、かつ元のdataframeに影響を及ぼす処理なしのため
            all_df = pd.concat(all_df_list, axis='index',
                               copy=False, sort=False)
            app.logger.info(f'shape of all dataframe: {all_df.shape}')
            df = all_df.sort_values(
                by="ai_score", ascending=False).reset_index(drop=True)
        except Exception as e:
            app.logger.error(f'predict error : {e}')
            return render_template('csv.html', fig=True, alert="予測に失敗しました。ファイルの種類やcsvのカラム・値に不正がないかご確認ください")

        try:
            if len(filename_list) == 1:
                save_filename = filename_list[0]
            else:
                basename_list = []
                for filename in filename_list:
                    basename, extention = os.path.splitext(filename)
                    basename_list.append(basename)
                save_filename = "--".join(basename_list) + '.csv'
            save_filename = '推論後_' + save_filename
            app.logger.info(f'saved file name: {save_filename}')
        except Exception as e:
            app.logger.error(f'filename error : {e}')
            return render_template('csv.html', fig=True, alert="ファイル名の加工に失敗しました。csvのファイル名に不正がないかご確認ください。")

        try:
            quoted_save_filename = quote(save_filename)
            resp = make_response(
                df.to_csv(encoding='utf-8').encode('shift_jis'))
            resp.headers["Content-Disposition"] = f"attachment;filename={quoted_save_filename};filename*=UTF-8''{quoted_save_filename};"
            resp.headers["Content-Type"] = "text/csv; charset=shift-jis"
            return resp

        except Exception as e:
            app.logger.error(f'download error : {e}')
            return render_template('csv.html', fig=True, alert="ファイルのダウンロードに失敗しました")


if __name__ == '__main__':
    app.debug = True
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=5000)
