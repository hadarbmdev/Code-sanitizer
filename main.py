import re
import random
import string
from flask import Flask, request, jsonify
from tools import api_logger

app = Flask(__name__)


def sanitize_code(code, config):
  var_pattern = config.get(
    'var_pattern', r'(?<=\bvar\s)\w+|(?<=\blet\s)\w+|(?<=\bconst\s)\w+')
  str_pattern = config.get('str_pattern',
                           r"(?<!['\"])(['\"][^'\n]*?['\"])(?!['\"])")
  identifier_pattern = config.get('identifier_pattern', r'\b\w+\b')

  # Generate a random string for sanitization
  def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

  # Map to store meaningful values and their sanitized counterparts
  meaningful_to_sanitized = {}
  sanitized_to_meaningful = {}

  def sanitize_match(match):
    if match.group() not in meaningful_to_sanitized:
      sanitized_value = generate_random_string(len(match.group()))
      meaningful_to_sanitized[match.group()] = sanitized_value
      sanitized_to_meaningful[sanitized_value] = match.group()
    return meaningful_to_sanitized[match.group()]

  # Replace meaningful values with sanitized values
  sanitized_code = re.sub(rf'{var_pattern}|{str_pattern}|{identifier_pattern}',
                          sanitize_match, code)

  response = {
    'sanitized_code': sanitized_code,
    'meaningful_to_sanitized': meaningful_to_sanitized,
    'sanitized_to_meaningful': sanitized_to_meaningful
  }
  return response


def unsanitize_code(sanitized_code, sanitized_to_meaningful):

  def unsanitize_match(match):
    sanitized_value = match.group()
    return sanitized_to_meaningful[sanitized_value]

  meaningful_code = re.sub(r'\b\w+\b', unsanitize_match, sanitized_code)
  return meaningful_code


# API route to sanitize the code
@api_logger
@app.route('/sanitize', methods=['POST'])
def sanitize():
  data = request.get_json()
  code = data.get('code')
  config = data.get('config', {})

  response = sanitize_code(code, config)
  return jsonify(response)


# API route to unsanitize the code
@api_logger
@app.route('/unsanitize', methods=['POST'])
def unsanitize():
  data = request.get_json()
  sanitized_code = data.get('sanitized_code')
  sanitized_to_meaningful = data.get('sanitized_to_meaningful')

  meaningful_code = unsanitize_code(sanitized_code, sanitized_to_meaningful)
  response = {'meaningful_code': meaningful_code}
  return jsonify(response)


def print_open_endpoints():
  print("Open endpoints:")
  for rule in app.url_map.iter_rules():
    if 'GET' in rule.methods or 'POST' in rule.methods:
      print(rule)


if __name__ == '__main__':
  print_open_endpoints()
  app.run()
