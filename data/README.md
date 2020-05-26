# Labeled New Word Data

`new_words_from_news.csv`: Labeled new words from news  
`new_words_from_ptt.csv`: Labeled new words from PTT

## Structure

| Field | Type | Length | Comment |
|---|---|---|---|
| id | `INT` | 11 |  |
| word | `VARCHAR` | 32 | 新詞 |
| length | `INT` | 11 | 新詞長度 |
| freq | `INT` | 11 | 詞頻 |
| pmi | `FLOAT` |  | PMI值 |
| entropy | `FLOAT` |  | 分歧亂度值 |
| dict_type | `INT` | 4 |  |
| articles_id | `TEXT` |  | 出現文件列表 |
| domain | `VARCHAR` | 11 | 詞彙分類 |
| domain_prob | `TEXT` |  | 分類機率 |
| validation | `INT` | 4 | 人工標記，1為新詞，0為非新詞 |
| origin | `VARCHAR` | 11 | 資料來源 |
| detect_time | `DATETIME` |  | 新詞出現時間 |
| create_time | `DATETIME` |  | 欄位創建時間 |
