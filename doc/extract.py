# derived from https://github.com/jeanralphaviles/comment_parser/blob/master/comment_parser/parsers/c_parser.py
# MIT license - https://github.com/jeanralphaviles/comment_parser/blob/master/LICENSE


from collections import namedtuple


Comment = namedtuple('Comment', ['comment', 'line', 'multiline'])


class FileError(Exception):
    pass


class UnterminatedCommentError(Exception):
    pass


def extract_comments(filename):
    """Extracts a list of comments from the given C family source file.
    Comments are represented with the Comment class found in the common module.
    C family comments come in two forms, single and multi-line comments.
        - Single-line comments begin with '//' and continue to the end of line.
        - Multi-line comments begin with '/*' and end with '*/' and can span
            multiple lines of code. If a multi-line comment does not terminate
            before EOF is reached, then an exception is raised.
    Note that this doesn't take language-specific preprocessor directives into
    consideration.
    Args:
        filename: String name of the file to extract comments from.
    Returns:
        Python list of Comment objects in the order that they appear in the file.
    Raises:
        FileError: File was unable to be open or read.
        UnterminatedCommentError: Encountered an unterminated multi-line
            comment.
    """
    try:
        with open(filename, 'r') as source_file:
            state = 0
            current_comment = ''
            comments = []
            line_counter = 1
            comment_start = 1
            while True:
                char = source_file.read(1)
                if not char:
                    if state is 3 or state is 4:
                        raise UnterminatedCommentError()
                    if state is 2:
                        # Was in single line comment. Create comment.
                        comment = Comment(current_comment, line_counter, False)
                        comments.append(comment)
                    return comments
                if state is 0:
                    # Waiting for comment start character or beginning of
                    # string.
                    if char == '/':
                        state = 1
                    elif char == '"':
                        state = 5
                elif state is 1:
                    # Found comment start character, classify next character and
                    # determine if single or multiline comment.
                    if char == '/':
                        state = 2
                    elif char == '*':
                        comment_start = line_counter
                        state = 3
                    else:
                        state = 0
                elif state is 2:
                    # In single line comment, read characters until EOL.
                    if char == '\n':
                        comment = Comment(current_comment, line_counter, False)
                        comments.append(comment)
                        current_comment = ''
                        state = 0
                    else:
                        current_comment += char
                elif state is 3:
                    # In multi-line comment, add characters until '*'
                    # encountered.
                    if char == '*':
                        state = 4
                    else:
                        current_comment += char
                elif state is 4:
                    # In multi-line comment with asterisk found. Determine if
                    # comment is ending.
                    if char == '/':
                        comment = Comment(
                            current_comment, comment_start, True)
                        comments.append(comment)
                        current_comment = ''
                        state = 0
                    else:
                        current_comment += '*'
                        # Care for multiple '*' in a row
                        if char != '*':
                            current_comment += char
                            state = 3
                elif state is 5:
                    # In string literal, expect literal end or escape char.
                    if char == '"':
                        state = 0
                    elif char == '\\':
                        state = 6
                elif state is 6:
                    # In string literal, escaping current char.
                    state = 5
                if char == '\n':
                    line_counter += 1
    except OSError as exception:
        raise FileError(str(exception))


if __name__ == '__main__':
    import sys
    from pprint import pprint

    pprint(extract_comments(sys.argv[1]))
