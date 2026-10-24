# Project KIMAGURE

ホームページプロジェクトの初期フォルダ構成です。

## ガラクタ置き場の更新

`garakuta/software.json` がソフト情報の編集元です。項目を追加するとソフトを増やせます。
編集後に `python scripts/build_garakuta.py` を実行し、生成された `garakuta/index.html` もコミットします。
静的HTMLのため、閲覧時のJavaScriptやGitHub API接続は不要です。

未公開の値は `null` とし、機能・対応OS・ライセンスは確認済みの内容だけ記載します。
スクリーンショットはリポジトリ内の実画像の相対パスを `screenshot` に指定します。
文章には「，」「．」を使用すると、その直後に改行が生成されます。

### インストーラーの公開

1. 動作確認済みの `.exe` または `.msi` をGitHub Releasesの正式リリースに添付します。大容量ファイルをこのサイトのGit管理に追加する必要はありません。ソフト本体のソースコード公開も不要です。
2. `version`、`updated`、`history`（文章の配列）、`license`、`status`、対応OSと機能を確定情報に更新します。
3. `release` を `{"repository": "flamecard/kimagure-no-yakata", "tag": "実際のタグ", "asset": "実際のインストーラー名.exe"}` に設定します。別の公開リポジトリのReleasesも指定可能です。
4. 生成コマンドを実行します。実在する非空の正式公開アセットをGitHub APIで確認できた場合のみダウンロードリンクを生成します。未設定の場合は公開待ちのままです。検証に失敗した場合はHTMLを書き換えずエラーで終了します。
5. 生成結果と実ファイルのダウンロードを確認して公開します。配布停止時は `release` を `null` に戻して再生成します。公開後のアセット削除はページを自動更新しないため、必ず同時にサイトも更新してください。

### インストール不要の小型ZIP

気まぐれQRは `assets/downloads/` 内のZIPを直接配布します。`portable_download` にリポジトリ内の `path` とファイルの `sha256` を設定すると，ファイルの存在・ハッシュ・ZIPの整合性・実行ファイルの同梱を確認してリンクを生成します。起動方法は「すべて展開」後に `KimagureQR.exe` を開く形です。

現行の `garakuta/index.html` には大会室の紹介と文節単位の折り返し調整が追加されています。全体を再生成する際は，それらの内容とサムネ工房の最新バージョンを維持してください。

## PC版の一項目だけを更新する

`python scripts/build_garakuta.py --only video-editor` は、公開中のPCページの対象カードと案内名だけを更新します。ほかのソフトの紹介、PC／スマホの切替、背景、スマホ版を変更しません。

KomaCutの配布ZIPはGitHub Releasesに掲載し、`release` に実アセットのタグ・名前・SHA256を指定します。`launch_executable` と `download_note` に起動方法と初回準備を記載してください。公開済みアセットと検査値が一致するときだけリンクを作ります。KomaCut本体の利用条件と、初回に提供元から取得するFFmpeg等の条件は区別して案内します。
