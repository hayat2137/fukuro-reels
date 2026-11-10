# fukuro-reels

@fukuro_hakase_mind（ふくろう博士）のリール動画置き場と制作スクリプト。
Metricool の予約投稿は `videos/` の動画を raw URL で読み込む。

- `scripts/setup_voicevox.sh` … VOICEVOX（ちび式じい）の準備
- `scripts/tts_q.py OUT_DIR LINES_JSON [kana]` … 台本 → 1文ごとの wav と durs.json（kana で読み確認）
- `scripts/quiz_render.py` … クイズ形式リールの映像の参考実装（テーマ部分は毎回書き換える）
- `videos/YYYY-MM-DD/` … その日の動画と台本

ふくろう博士の画像は claude.ai の Project ファイル（IMG_1852 通常 / IMG_1851 口開き / IMG_1850 目閉じ）を使う。
音声: VOICEVOX:ちび式じい
