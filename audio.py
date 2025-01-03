from common import extract_video_url, print_dedent, run_command
import const


def download_audio(url, format, saveDir=None):
    format_map = {"wav": "2", "mp3": "3"}
    if format not in format_map:
        return

    print_dedent(
        """
        音声のダウンロードを開始します
        """,
        "\n",
    )

    target_url = extract_video_url(url)
    if not target_url:
        print_dedent(
            """
            URLが不正です
            """
        )
        print(f"入力されたURL: {url}")
        print()
        print("エンターを押して続行...")
        input()
        return

    output = f'-o "{saveDir}/%("title")s.%(ext)s"' if saveDir else ""
    run_command(f"{const.command_list[format_map[format]]['command']} {output} {target_url}")
    print(f"target_url: {target_url}")


def download_audio_wav(url, saveDir=None):
    download_audio(url, "wav", saveDir)


def download_audio_mp3(url, saveDir=None):
    download_audio(url, "mp3", saveDir)
