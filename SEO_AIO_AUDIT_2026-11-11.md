# SEO・AI検索 点検記録

2026年11月11日（日本時間）

## 今回の修正
配線・小型机・引き出しの独立ガイド3本が別記事をcanonical指定していた不整合を修正。about/check/privacyにも正規URLを設定。404をnoindex化。

- Cloudflare Pagesの仕様に合わせcanonical・sitemap・JSON-LDのページURLを拡張子なしへ統一。独立記事は自己参照canonical。
- 構造化データに架空の評価、使用体験、公開日・更新日は追加していない。既存FAQと本文の一致を検査。
- 404はnoindex。トップレベル404のない静的サイトには追加し、存在しないURLがトップを返すSPAフォールバックを防止。
- 内部リンクの存在、JSON-LDの構文、h1数、description、canonical一意性、サイトマップ整合、Google所有権確認ファイル不変を検査。
- A8・バリューコマース広告のアンカー・画像と計測ピクセルは変更前と一致。

## 範囲・未確認事項
- 本記録は技術SEOと本文・構造化データの整合の点検。全商品仕様・補助金制度・購入者レビューの再取材ではない。
- Search Consoleの登録数・検索順位・AI検索での引用率は未確認。Google上位表示や引用は保証しない。
- CDN側のbot制御、WAF、旧ホストからの転送はリポジトリだけでは確認できない。
- 商品別のASIN未照合・レビュー件数未検証などの保留状態は、既存方針に従い残す。

## 根拠
- https://developers.google.com/search/docs/appearance/ai-features
- https://developers.cloudflare.com/pages/configuration/serving-pages/

## 2026年11月12日：購入前記事の内容改善

代表的な購入前チェック記事1本に、対象別の確認表（何を調べ、どの点に注意して判断するか）と関連記事を追加。編集更新日を本文に明示。価格・商品仕様・レビュー・制度の再確認日とは区別する。広告アンカーと画像・計測要素の不変、関連記事の存在、主見出し、JSON-LD構文を検査。坂道は更新用ソースに組み込み、再ビルドで保持。
