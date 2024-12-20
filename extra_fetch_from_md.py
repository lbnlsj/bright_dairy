import re
import json
import pyperclip


def extract_fetch_blocks(md_content):
    """Extract fetch code blocks from markdown content."""
    # Look for code blocks that start with fetch
    fetch_blocks = re.finditer(r'```js\n(fetch\(.*?\);)\n```', md_content, re.DOTALL)
    return list(fetch_blocks)


def parse_fetch_request(fetch_block):
    """Parse a fetch block into url and options."""
    # Extract the fetch arguments
    fetch_content = fetch_block.group(1)

    # Split into URL and options
    first_comma = fetch_content.find(',', fetch_content.find('"'))
    url = fetch_content[:first_comma].strip().strip('"')[7:]
    options = fetch_content[first_comma + 1:].strip()

    # Parse the options JSON
    try:
        options_dict = json.loads(options[:-2])
        return url, options_dict
    except json.JSONDecodeError:
        return None, None


def convert_to_requests(url, options):
    """Convert fetch options to requests code."""
    if not url or not options:
        return None

    method = options.get('method', 'GET')
    headers = options.get('headers', {})
    body = options.get('body')

    # Format the code
    func_name = url.split("/")[-1].replace('-', '_').replace('&', '_').replace('=', '_').replace('?', '')
    func_name = func_name[:10] if len(func_name) > 10 else func_name
    code_lines = [
        f'def {func_name}():',
        '',
        f'    url = "{url}"',
        '',
        '    headers = {',
    ]

    # Add headers
    for key, value in headers.items():
        value = value.replace('"', '\\"')
        code_lines.append(f'        "{key}": "{value}",')
    code_lines.append('    }')
    code_lines.append('')

    # Add body if exists
    if body:
        try:
            # Parse the body if it's JSON
            body_dict = json.loads(body)
            code_lines.append('    data = {')
            for key, value in body_dict.items():
                # Use repr to properly handle nested quotes
                code_lines.append(f'        "{key}": {repr(value)},')
            code_lines.append('    }')
            code_lines.append('')
            data_var = 'json=data'
        except json.JSONDecodeError:
            code_lines.append(f'    data = {repr(body)}')
            code_lines.append('')
            data_var = '    data=data'
    else:
        data_var = ''

    # Add the request
    request_line = f'    response = session.{method.lower()}(url, headers=headers'
    if data_var:
        request_line += f', {data_var}'
    request_line += ')'
    code_lines.append(request_line)
    code_lines.append('\n    print(response.status_code)\n\n    return response.text')

    return '\n'.join(code_lines)


def main(md_content):
    """Main function to process markdown and convert fetch to requests."""
    fetch_blocks = extract_fetch_blocks(md_content)
    all_code = ['import requests', '', 'session = requests.session()', '']

    for block in fetch_blocks:
        url, options = parse_fetch_request(block)
        requests_code = convert_to_requests(url, options)
        if requests_code:
            all_code.append(requests_code)
            all_code.append('\n' + '#' * 50 + '\n')  # Separator between requests
    all_code.append(f'\nif __name__ == "__main__":')
    for code in all_code:
        first_func_name = re.match('def (.*?\(\))', code)
        if not first_func_name: continue
        all_code[-1] += f'\n\n    {first_func_name.group(1)}'

    final_code = '\n'.join(all_code)
    pyperclip.copy(final_code)
    return final_code


# Example usage
if __name__ == "__main__":
    with open('readme.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    converted_code = main(md_content)
    print("Converted code has been copied to clipboard!")
    print("\nPreview of the converted code:")
    print(converted_code)
    open('fetch.py', 'w').write(converted_code)