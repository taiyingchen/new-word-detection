# new-word-detection

New word detection for Chinese

## Installation

```sh
git clone https://github.com/taiyingchen/new-word-detection
cd new-word-detection/
pip3 install .
```

Create `.env` file

```sh
cd new-word-detection/
cp .env.example .env
```

`.env` example

```txt
[DEFAULT]
stopwords_path = dict/stopwords.txt
prep_path = dict/preposition.txt
jieba_dict_path = PATH_TO_JIEBA_DICTIONARY
user_dict_path = PATH_TO_USER_DICTIONARY
blacklist_path = PATH_TO_BLACKLIST
```

## Usage

```python
from nwd.new_word_detection import NWD

# `docs` is a list of str, each element is a document
docs = ['第一篇文件', '第二篇文件', '第三篇文件']

nwd = NWD(max_len=3, min_freq=10, min_pmi=3, min_entropy=3)
new_words = nwd.fit_detect(docs)
```
