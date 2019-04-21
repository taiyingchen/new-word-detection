# new-word-detection

New word detection for Chinese

## Installation

```sh
git clone https://github.com/taiyingchen/new-word-detection
cd new-word-detection
pip install -r requirements.txt
```

## Usage

```python
from nwd.new_word_detection import NWD

# `docs` is a list of str, each element is a document
docs = ['第一篇文件', '第二篇文件', '第三篇文件']

nwd = NWD(max_len=3, min_freq=10, min_pmi=3, min_entropy=3)
new_words = nwd.fit_detect(docs)
```
