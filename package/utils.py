import os


def get_absolute_path(*res):
    return os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(__file__), *res))


def get_dict(dict_file):
    kw_dict = set()
    with open(dict_file, 'r') as file:
        for line in file:
            kw_dict.add(' '.join(line.split()[:-1]))
    return kw_dict


def get_list(list_file):
    return_list = []
    with open(list_file, 'r', encoding='utf8') as file:
        for line in file:
            return_list.append(line.strip())
    return return_list


def get_sistring(file, sistring=set()):
    with open(file, 'rb') as f:
        for lineno, line in enumerate(f, 1):
            try:
                line = line.strip().decode('utf-8')
                word = line.split(' ')[0]
                for ch in range(len(word)):
                    if word[ch:] not in sistring:
                        sistring.add(word[ch:])
            except ValueError:
                raise ValueError(
                    'invalid dictionary entry in %s at Line %s: %s' % (file, lineno, line))
    return sistring


def check_docs(docs):
    """Input validation on documents

    """
    if docs is None:
        raise ValueError('docs cannot be None')

    if not isinstance(docs, list):
        raise TypeError('docs must be list of string')

    for doc in docs:
        if not isinstance(doc, str):
            raise TypeError('docs must be list of string')
