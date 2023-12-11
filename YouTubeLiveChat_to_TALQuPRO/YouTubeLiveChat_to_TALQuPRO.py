# YouTubeLiveChat_to_TALQuPRO (YouTubeLiveコメ読みするよ)
# ver 1.1.0
# The MIT License
# Copyright 2023 Haruqa

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import sys
sys.path.append('')
import pytchat
import time
import subprocess
import os
import re

def hankakuToZenkaku(message):
    message = message.translate(str.maketrans({chr(0x0021 + i): chr(0xFF01 + i) for i in range(94)}))
    return message

def play(exe_path, 使うモデル, message):
    #再生実行のみを行う例)TALQuPRO_CMDClient.exe Haruqa,dummy,読み上げたいテキスト,,only
    #再生が完了するまで待機となる
    if(message!=""):
        subprocess.run(exe_path + " " + 使うモデル + ",dummy," + message + ",,only", shell=True)
        time.sleep(0.5)

def message_process(message):
    #（）()読み飛ばし処理
    message = re.sub('（.+）','',message)
    message = re.sub('\(.+\)','',message)
    #記号処理
    message = re.sub(':.+:','',message)
    message = re.sub('っ+','っ',message)
    message = re.sub('ッ+','ッ',message)
    message = re.sub('？*！+？+','？',message)
    message = re.sub('[?❓❔⁉️]+','？',message)
    message = re.sub('[!！❗❕‼️・…‥]+','。',message)
    message = re.sub('？*！+？+','？',message)
    message = re.sub('[～~]','ー',message)
    message = re.sub('[., 　\\⁄:*"|]', '、', message)
    message = re.sub('[※\#＃\'’"”＊×÷＋+\-:;*：；＞＜><【】『』「」\[\]｛｝\{\}]', '', message)
    message = re.sub('^[！？、。]+$', '', message)
    #w処理
    message = re.sub('笑+', 'わらわら', message)
    message = re.sub('[ｗw]', 'わら', message)
    #半角処理
    message = hankakuToZenkaku(message)
    return message

def setting():
    print("TALQuPRO_CMDClient.exeをこの画面にドラッグ＆ドロップしてEnterを押してください")
    while True:
        exe_path = input()
        if(exe_path.endswith("TALQuPRO_CMDClient.exe")):
            break
        else:
            print("TALQuPRO_CMDClient.exeではありません")

    # バージョン取得コマンド
    result_for_version = subprocess.run(exe_path + " getVersion", shell=True, stdout=subprocess.PIPE, text=True)
    version_list = str(result_for_version.stdout).replace("\n","").split(".")
    # 動作確認したバージョンは2.2.0
    if(version_list[0] != "2"):
        print("強制終了：対応するTALQuPRO_CMDClient.exeとバージョンが異なるため終了します。更新情報を確認してください。")
        os._exit(0)
    if(version_list[1] != "2" or version_list[2] != "0"):
        print("警告：処理を続行しますが、動作を確認したTALQuPRO_CMDClient.exeとバージョンが異なるため想定する動作と異なる可能性があります。更新情報を確認してください。")

    # 利用可能話者名取得コマンド
    subprocess.run(exe_path + " getSpkName", shell=True)

    print("使用したいモデル名を入力してEnterを押してください、入力なしでEnterでデフォルトのHaruqaが使用されます")
    使うモデル = input()
    if(使うモデル == ""):
        使うモデル = "Haruqa"

    print("読み上げ最大文字数を入力してEnterを押してください、入力なしでEnterでデフォルトの100が使用されます")
    読み上げ最大文字数 = input()
    if(読み上げ最大文字数 == ""):
        読み上げ最大文字数 = 100
    else:
        読み上げ最大文字数 = int(読み上げ最大文字数)

    print("テスト音声出力")
    play(exe_path , 使うモデル, "マイクテスト")

    print("配信のURLを入力してEnterを押してください、コメント読み上げを開始します")
    配信のID = input()

    return exe_path, 使うモデル, 読み上げ最大文字数, 配信のID

def main(livechat, exe_path, 使うモデル, 読み上げ最大文字数):
    print("コメント待機開始…")
    pre_message = ""
    while livechat.is_alive():
        # チャットデータの取得
        chatdata = livechat.get()
        played_flg = False
        for c in chatdata.items:
            message = str(c.message)
            if(pre_message != message):
                print(message)
                message = message_process(message)
                message = hankakuToZenkaku(message)
                if len(message) >= 読み上げ最大文字数:
                    message = message[:読み上げ最大文字数] + "、省略しました"
                try:
                    played_flg = True
                    play(exe_path, 使うモデル, message)
                except:
                    print("コメントが読めませんでした")
                pre_message = message
            else:
                print("コメントが同一のため読み飛ばします")

        if played_flg == False:
            time.sleep(1)
    print("終了しました")

if __name__ == '__main__':
    # TALQu→クライアントへの処理結果メッセージ送信のための接続待機で固まってしまうのが回避できていないので、
    # ひとまず注意書きを書いておく
    print("注意：処理途中で強制終了した後再起動する場合、正常に動作しないことがあります。")
    print("　　　この場合、TALQu本体を再起動してください。")
    try:
        exe_path, 使うモデル, 読み上げ最大文字数, 配信のID = setting()

        while True:
            # PytchatCoreオブジェクトの取得
            livechat = pytchat.create(video_id = 配信のID)
            if(livechat.is_alive()):
                break

        main(livechat, exe_path, 使うモデル, 読み上げ最大文字数)
    except Exception as err:
        print(err)
        print("例外が発生したため終了します。操作をやり直してください。")

