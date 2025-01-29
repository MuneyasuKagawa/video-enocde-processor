import os
import librosa
import soundfile as sf
import numpy as np
from scipy.signal import correlate, butter, sosfilt
from common import clear_screen, print_dedent

# 音声ファイルの読み込み
def load_audio(file_path):
    audio, sr = librosa.load(file_path, sr=None, mono=False)
    return audio, sr

# クロスコリレーションを用いて一致度を測定
def find_best_shift(original, instrumental):
    correlation = correlate(original, instrumental, mode='full')
    shift = np.argmax(correlation) - (len(instrumental) - 1)
    return shift

# 周波数ドメインでの位相差を利用
def find_best_shift_fft(original, instrumental):
    # チャンネルごとにシフトを計算
    shifts = []
    for ch in range(original.shape[0]):
        # FFTを使用して位相差を計算
        orig_fft = np.fft.fft(original[ch])
        inst_fft = np.fft.fft(instrumental[ch])
        
        # 位相差を計算
        phase_diff = np.angle(orig_fft) - np.angle(inst_fft)
        
        # 逆FFTで時間差を推定
        correlation = np.fft.ifft(np.exp(1j * phase_diff))
        shift = np.argmax(np.abs(correlation))
        
        if shift > len(original[ch]) // 2:
            shift -= len(original[ch])
        
        shifts.append(shift)
    
    # 全チャンネルの平均シフト値を返す（整数に丸める）
    return int(np.mean(shifts))

# 音声を時間シフトする関数
def shift_audio(audio, shift):
    if shift == 0:
        return audio
    
    shifted_audio = np.zeros_like(audio)
    for i in range(audio.shape[0]):
        if shift > 0:
            shifted_audio[i, shift:] = audio[i, :-shift]
        else:
            shifted_audio[i, :shift] = audio[i, -shift:]
    return shifted_audio

def apply_highpass_filter(audio, sr, cutoff_freq=120):
    # バターワースフィルターのパラメータを計算
    nyquist = sr / 2
    normalized_cutoff_freq = cutoff_freq / nyquist
    sos = butter(6, normalized_cutoff_freq, btype='high', output='sos')
    
    # 各チャンネルにフィルターを適用
    filtered_audio = np.zeros_like(audio)
    for ch in range(audio.shape[0]):
        filtered_audio[ch] = sosfilt(sos, audio[ch])
    
    return filtered_audio

def ms_processing(audio):
    if audio.shape[0] != 2:
        raise ValueError("ステレオ音声が必要です")
    
    left = audio[0]
    right = audio[1]

    # 中央成分とサイド成分を正確に計算
    mid = (left + right) / 2.0  # 中央成分
    side = (left - right) / 2.0  # サイド成分

    # ステレオ定位を維持したMS処理
    side = audio[0] - audio[1]
    mid = audio[0] + audio[1]
    mid *= 0.2
    
    left_new = mid + side     # = side
    right_new = mid - side    # = -side
    
    return np.array([left_new, right_new])

# メイン処理
def extract_vocal(output_dir):
    clear_screen()

    audio_files = [
        f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f)) and( f.endswith(".wav") or f.endswith(".mp3"))
    ]
    if not audio_files:
        print_dedent(
            """
            .wavファイルが存在しません
            """
        )
        print(f"対象フォルダ: {output_dir}")
        print()
        return

    for i, audio_file in enumerate(audio_files):
        print(f"{i}) {audio_file}")

    original_index = None
    while True:
        print_dedent(
            """
            
            オリジナル音源ファイルを選択してください
            選択: """
        )
        original_index = input()
        if not original_index.isdigit() or int(original_index) >= len(audio_files):
            continue
        break

    original_file = os.path.join(output_dir, audio_files[int(original_index)])

    clear_screen()
    for i, audio_file in enumerate(audio_files):
        print(f"{i}) {audio_file}")

    inst_index = None
    while True:
        print_dedent(
            """
            
            インスト音源ファイルを選択してください
            選択: """
        )
        inst_index = input()
        if not inst_index.isdigit() or int(inst_index) >= len(audio_files):
            continue
        break

    instrumental_file = os.path.join(output_dir, audio_files[int(inst_index)])


    mode = None
    while True:
        clear_screen()
        print("1) クロスコリレーション")
        print("2) 周波数ドメイン")
        print_dedent(
            """
            
            抽出モードを選択してください
            選択(デフォルト:2): """
        )
        mode = input().strip()
        if mode == "":
            mode = "2"
            break
        elif mode in ["1", "2"]:
            break

        continue

    clear_screen()

    # 上書き確認
    if os.path.exists(f"{output_dir}/vocal_output.wav"):
        print_dedent("""\
            出力ファイルが存在します
            上書きしますか？(Y/n): """
        )
        overwrite = input().lower()
        if overwrite == "n":
            return

    print_dedent(
        """
        ボーカルを抽出しています...

        """
    )

    original, sr = load_audio(original_file)
    instrumental, _ = load_audio(instrumental_file)

    # 長さを揃える
    min_length = min(original.shape[1], instrumental.shape[1])
    original = original[:, :min_length]
    instrumental = instrumental[:, :min_length]

    # 一致度を測定して最適なシフトを計算
    if mode == "1":
        best_shift = find_best_shift(original, instrumental)
    else:
        best_shift = find_best_shift_fft(original, instrumental)
    print(f"Best shift: {best_shift} samples")

    # 音声をシフト
    aligned_instrumental = shift_audio(instrumental, best_shift)

    # ボーカルの抽出 (各チャンネルごとに差分を計算)
    vocal = original - aligned_instrumental

    # ハイパスフィルターを適用
    vocal_filtered = apply_highpass_filter(vocal, sr, cutoff_freq=200)

    # 結果を保存
    output_file = f"{output_dir}/vocal_output.wav"
    sf.write(output_file, vocal_filtered.T, sr)  # 転置が必要
    print_dedent(
        f"""
        ボーカル音声を '{output_file}' に保存しました。

        サイド成分の抽出を行いますか？(y/N): """
    )

    # サイド成分の抽出
    side = input().lower()
    if side == "y":
        print_dedent(
            """
            サイド成分の音声を抽出しています...

            """
        )
        side_file = f"{output_dir}/vocal_output_side.wav"
        side_output = ms_processing(vocal_filtered)
        sf.write(side_file, side_output.T, sr)
        print(f"サイド成分の音声を '{side_file}' に保存しました。")
