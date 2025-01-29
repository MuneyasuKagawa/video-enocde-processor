command_list = {
    "1": {
        "label": "動画DL",
        "command": f"yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio --merge-output-format mp4",
    },
    "2": {
        "label": "音声DL(wav)",
        "command": f"yt-dlp -f bestaudio -x --audio-format wav",
    },
    "3": {
        "label": "音声DL(mp3)",
        "command": f"yt-dlp -f bestaudio -x --audio-format mp3 --audio-quality 320K",
    },
    "4": {
        "label": "エンコード(音声差し替え)",
        "command": 'ffmpeg -i "{{movie_input}}" -itsoffset {{offset}} -i "{{audio_input}}" -c:v copy -c:a aac -b:a 320k -strict experimental -map 0:v -map 1:a "{{output}}"',
    },
    "5": {
        "label": "ボーカル抽出",
        "command": "",
    },
    "6": {
        "label": "作業フォルダ変更",
        "command": "",
    },
    "q": {
        "label": "終了",
        "command": "exit",
    },
}
lastPathFileName = "last_save_dir"
