# gakkun2

子ども（2026/10時点で小学4年生・学習障害あり）向けの学習強制アプリ。Windows 常駐（タスクトレイ）で、
一定間隔ごとに全画面・最前面の出題ウィンドウを出し、正解するまで閉じられない。正解するとお小遣いが加算される。

## 実行

```
pip install -r requirements.txt
python main.py                 # 起動（多重起動は黙って終了）
python main.py --list-monitors # モニタ一覧
python main.py --monitor 2     # 出題を表示するモニタを指定
python install_autostart.py    # スタートアップ登録（dist/Gakkun2.exe があればそちら）
```

テストコードは無い。ロジック確認は `quiz_app` を直接 import して検証し、
画面確認は `quiz_window.show_quiz()` を一時的な Tk ルートで呼んで `PIL.ImageGrab` でスクリーンショットを撮る。

## 構成

| ファイル | 役割 |
|---|---|
| `main.py` | 起動、引数処理、Tk ルート作成、トレイ・スケジューラ起動 |
| `quiz_app/scheduler.py` | 出題タイミング管理。正解後 `interval_minutes` で次の定期出題、誤答時は `retry_minutes` 後に同じ問題を再出題。スコア・お小遣いの保存、出金 |
| `quiz_app/questions.py` | 出題の選択。カテゴリ（掛け算/割り算/漢字）を均等に選び、その中で重み付きランダム。漢字はレベル制 |
| `quiz_app/quiz_window.py` | 全画面の出題ウィンドウ。漢字は例文を表示し、対象語に下線 |
| `quiz_app/excel_data.py` | `kanji.xlsx` の読み込み（`KanjiEntry`） |
| `quiz_app/scores.py` | `scores.json` の読み書き。点数は -3〜5 にクランプ |
| `quiz_app/allowance.py` | `allowance.json`（獲得金額）の読み書き |
| `quiz_app/tray.py` | トレイメニュー（今すぐ出題・出金・終了[パスワード付き]） |
| `quiz_app/config.py` | `config.json` の読み込み。`DEFAULTS` にマージされるので新しい設定は `DEFAULTS` に追加する |
| `quiz_app/ime_control.py` | 漢字問題では IME をオン、算数ではオフにする |
| `quiz_app/music.py`, `celebration.py` | 放置時の音楽、正解時の効果音・紙吹雪 |

## データ

- `kanji.xlsx`（リポジトリ管理）: 先頭シート「問題」の列 `レベル | 例文 | 読み`。
  - 例文は読ませる語だけを全角 `［］` で囲み、それ以外はひらがな＋分かち書き（例: `がっこうには たくさんの ［人］が いる`）。
  - 読みは `［］` 内の語全体の読み（送り仮名込み）。複数正解は `/` 区切り。
  - レベル: 1=1年訓, 2=1年音・熟語, 3=2年訓, 4=2年音・熟語, … 8=4年音・熟語。熟語のレベルは含まれる最も高学年の漢字で決める。
- `scores.json`, `allowance.json`, `gakkun2.log*`（git 管理外）: 実行時に作成。
  - スコアキー: `multiplication:a:b`, `division:除数:商`, `kanji:語:最初の読み`。例文を変えてもキーは変わらない。`kanji.xlsx` から消えた語のスコアは自動削除される。

## 出題ロジックの意図（変更時に壊さないこと）

- **さぼり対策**: 誤答・空欄エンター時は正解を表示し、その正解を入力するまで閉じられない（書き写し後も結果は不正解扱い）。`WM_DELETE_WINDOW` は無効化している。
- **同じ問題ばかり出る問題の対策**: 点数は -3 が下限。最低点の問題だけを出すのではなく重み付きランダム（苦手・未出題ほど出やすい）にし、直近5問は避ける。
- **やさしい順**: 漢字は易しいレベルから。現在レベルの問題の `level_up_ratio`(0.8) 以上が `mastery_score`(1) 点以上になると次のレベルが加わる。
- 子ども向け表示文はひらがな多め・分かち書きにする。

## 注意

- Windows 専用（ctypes で imm32、pywin32、pystray）。
- 改行コードは CRLF 化の警告が出るが、既存どおりでよい。
