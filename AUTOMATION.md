# 毎日の自動投稿手順（ふくろう博士 @fukuro_hakase_mind）

毎晩1回実行し、**翌日（日本時間）**の10:00と18:00に投稿するリール2本を作って Metricool に予約する。
確認なしで公開されるので、下の「止める条件」に1つでも当たったら予約せず報告して終わる。

## 0. 準備
1. `add_repo` で hayat2137/fukuro-reels（push）を追加し `/home/claude/fukuro-reels` に clone
2. `bash scripts/setup_voicevox.sh`
3. フォント: `/usr/share/fonts/opentype/noto/NotoSansCJK-{Black,Bold}.ttc` が無ければ `apt-get install -y fonts-noto-cjk`
4. ふくろう画像は `assets/owl_{normal,open,blink}_hd.png`（ユーザー提供。自分で描かない）

## 1. 二重予約の確認
- 対象日 = 実行日の翌日（Asia/Tokyo）
- Metricool `getScheduledPosts`（brandId 7871661, timezone Asia/Tokyo）で対象日に Instagram の予約が既にあれば何もせず終了

## 2. 分析
- `insta-analysis` スキルに従い分析し、レポート（ドキュメント）を作る
- Metricool の投稿日時 IGRE02 は UTC。+9時間で日本時間
- `state.json` の themes の種類（A=分析ネタ / B=新テーマ）で A と B を比べ、新テーマを 採用/保留/不採用 で判定

## 3. ネタ2本
- `insta-neta` スキルに従う。A=分析レポートの引き継ぎ事項どおり、B=未使用の幅広い新テーマ
- 作り（クイズ形式「AとB、どっち？」、答えは後半、6シーン、約20秒、締め「当たったら、友達にも出題してくれ」）は A と B でそろえ、テーマだけ変える（分析で別の作りが推奨されたら、それに2本ともそろえる）
- `state.json` の themes / rejected_themes と被らない。特定の人だけに当てはまる狭いテーマは避ける
- 数字・雑学は必ず一次情報か信頼できる媒体で確認。裏付けのない話は使わない
- 投稿時間: `state.json` の last_A_time と入れ替える（前回 A=10:00 なら今回 A=18:00, B=10:00）

## 4. 動画
1. `python3 scripts/tts_q.py <work>/audio <work>/lines.json kana` で全文の読みを確認。誤読は表記を変える（例: 4分の1→よんぶんのいち、ナサ→NASA）
2. 読みが正しければ `kana` なしで生成。データの文は1文5秒以内
3. `scripts/quiz_render.py` を作業フォルダに写し、ROOT・出力名・テーマ部分（タイトル、選択肢、各シーン、背景、色、保存用カード）を書き換える。背景はテーマをイメージした絵（黒一色にしない）
4. `preview` で6枚の静止画を作り、Read で目視確認。文字が x80〜1000 からはみ出していないか、重なっていないか、内容が台本と合うかを確認し、直してから `full` を1回
5. `ffprobe` で映像と音声の長さが一致することを確認

## 5. アップロード
- `videos/<対象日>/` に mp4 と lines.json を置き commit・push（main）
- 動画URL: `https://raw.githubusercontent.com/hayat2137/fukuro-reels/main/videos/<対象日>/<ファイル名>.mp4`

## 6. 予約（Metricool createScheduledPost）
- blogId "7871661"、providers [{"network":"instagram"}]、instagramData.type "REEL"、showReelOnFeed true
- publicationDate {"dateTime":"<対象日>T10:00:00" または T18:00:00, "timezone":"Asia/Tokyo"}、date も同じ時刻（+09:00）
- media [動画URL]、text = キャプション全文（VOICEVOX:ちび式じい のクレジット必須）、autoPublish true、draft false
- BGM: instagramData.audioConfiguration {"audioId":"<BGM候補の検索語>", "audioVolume":15, "videoVolume":100}。候補が複数返ったら合う曲の数字IDで再試行。アカウント条件などで拒否されたら audioConfiguration を外して予約し、そのことを報告に書く

## 7. 記録と報告
- 「投稿ネタ_<対象日>」ドキュメントを作る（insta-neta スキルの出力形式。どちらがA/Bか、何時投稿かを明記）
- `state.json` を更新（last_post_date、last_A_time、themes に2本追加。B の判定結果が出たら該当行に result を追記）し push
- SendUserMessage で報告: 2本のテーマ・投稿時刻・plannerUrl・ドキュメントのリンク・BGM の有無。動画ファイルも SendUserFile で送る

## 止める条件（予約しない）
- 出典が確認できない数字がある / 読み間違いが直らない / 文字のはみ出し・重なりが直らない / 映像と音声の長さが合わない / push に失敗した
- この場合は作ったところまでを報告し、何が問題かを書く
