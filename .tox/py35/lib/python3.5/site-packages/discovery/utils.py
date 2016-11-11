import re
import logging
logger = logging.getLogger(__name__)


def parseMessage(data):
    headers = {}
    encodedLines = list(filter(lambda l: l != '', data.splitlines()))
    lines = [line.decode('utf-8') for line in encodedLines]
    first_line, rest_lines = lines[0], lines[1:]

    for line in rest_lines:
        try:
            str_line = line
            tokens = str_line.split(':', 1)
            if len(tokens) < 2:
                continue
            (key, dirty_value) = tokens
            value = re.sub(r'^\s', '', dirty_value)
        except Exception as e:
            logger.error(e)
            logger.error(str_line.split(':', 1))
            logger.error(lines)
        else:
            headers[key] = value

    headers['method'] = first_line.split(' ')[0]

    return headers


def build_message(messageHeaders):
    return '\r\n'.join(messageHeaders).encode('utf-8')

#
# def parseMessage(data):
#     headers = {}
#     lines = [line.strip() for line in data.splitlines()]
#     for line in lines[1:]:
#         try:
#             str_line = line.decode('utf-8')
#             tokens = str_line.split(':', 1)
#             if len(tokens) < 2: continue
#
#             key, value = tokens
#         except Exception as e:
#             logger.error(e)
#             pass
#         else:
#             headers[key] = value
#
#     headers['method'] = lines[0].split()[0].decode('utf-8')
#
#     return headers
