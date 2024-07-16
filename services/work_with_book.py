book_path = 'books/book.txt'
book: dict[int, str] = {}
PAGE_SIZE = 1050


def _get_part_text(text: str, start: int, size: int) -> (str, int):
    """ Возвращает строку """
    if start + size >= len(text):
        result = text[start:]
    else:
        end_string = ',.!:;?'
        while size:
            if text[start + size - 1] in end_string and text[start + size] not in end_string:
                break
            size -= 1
        result = text[start:start + size]
    return result, len(result)


def prepare_book(path: str = book_path) -> None:
    page = 1
    start = 0
    with open(path, 'r', encoding='utf-8') as file:
        books = file.read()

    while start < len(books):
        text, size = _get_part_text(books, start, PAGE_SIZE)
        book[page] = text.lstrip()
        start += size
        page += 1
