from common import extract_video_url, print_dedent, run_command
import const


def download_movie(url, saveDir=None):
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

    print_dedent(
        """
        動画のダウンロードを開始します
        """,
        "\n",
    )
    output = f'-o "{saveDir}"' if saveDir else ""
    run_command(f"{const.command_list['1']['command']} {target_url} {output}")
    print(f"target_url: {target_url}")
