import requests
from bs4 import BeautifulSoup
import json
import os
from tqdm import tqdm

##################################### Globals #####################################

BASE = "https://www.scu.edu/bulletin/undergraduate"
URL = "https://www.scu.edu/bulletin/undergraduate/"
HTML_DIR_PATH = "data/html/"
SUBLINKS_PATH = "data/bulletin/sublinks.txt"
DATAFILE_PATH = "data/bulletin/output.json"

##################################### bs4 #####################################

def make_soup(url):
    global soup
    headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9"}
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.content, 'html5lib')
    return soup

##################################### HTML Attribute Functions #####################################
    
def getHTML(soup : BeautifulSoup):
    os.makedirs(HTML_DIR_PATH, exist_ok=True)
    file_name = f"{htmls_generated}.html"
    out_file_path = os.path.join(HTML_DIR_PATH, file_name)

    with open(out_file_path, "w") as html_file:
        html_file.write(soup.prettify())
    
    return out_file_path

def remove_elements_by_tag(tag_names: list):
    for tag_name in tag_names:
        elements = soup.find_all(tag_name)
        if elements:
            for element in elements:
                element.extract()

def remove_elements_by_tag_and_class(tag, class_):
    tag_type = soup.find(tag, class_)
    if tag_type:
        tag_type.extract()

def surround_tag_with_span(tag, span='span'):
    tag_collection = soup.find_all(tag)
    if tag_collection:
        for item in tag_collection:
            new_span_before = soup.new_tag(span)
            new_span_before.string = f"\n<{tag}>\n"
            item.insert_before(new_span_before)

            new_span_after = soup.new_tag(span)
            new_span_after.string = f"\n</{tag}>\n"
            item.insert_after(new_span_after)

def surround_ul_with_span(tag, span='span'):
    tag_collection = soup.find_all(tag)
    if tag_collection:
        for ul in tag_collection:
            new_span_before = soup.new_tag(span)
            new_span_before.string = f"\n<{tag}>\n"
            ul.insert_before(new_span_before)

            li_list = soup.find_all('li')
            if li_list:
                for li in li_list:
                    new_li_before = soup.new_tag(span)
                    new_li_before.string = f"<li>"
                    li.insert_before(new_li_before)

                    new_li_after = soup.new_tag(span)
                    new_li_after.string = f"</li>"
                    li.insert_after(new_li_after)

            new_span_after = soup.new_tag(span)
            new_span_after.string = f"\n</{tag}>\n"
            ul.insert_after(new_span_after)

def refactor_html():
    # Tag Removal
    remove_elements_by_tag(['a', 'select', 'title', 'form', 'nav', 'footer', 'script', 'label', 'figcaption', 'style']) # general
    remove_elements_by_tag(['h4', 'h5']) # headers
    
    remove_elements_by_tag_and_class('div', 'modal')
    remove_elements_by_tag_and_class('li', 'breadcrumb-item')
    remove_elements_by_tag_and_class('span', 'pagetitle')

    # Span Insertion
    surround_ul_with_span('ul')
    surround_tag_with_span('h1')
    surround_tag_with_span('h2')
    surround_tag_with_span('h3')
    surround_tag_with_span('p')
    
    content = ""
    raw = soup.get_text()
    lines = raw.split('\n')
    pruned = [line.strip() for line in lines if line.strip()]
    content += '\n'.join(pruned)
    
    return content

def map_HTML_to_JSON(html_string, tag_list=['h1', 'h2', 'h3', 'p', 'ul']):
    base_json_dict = {}
    html = BeautifulSoup(html_string, 'html5lib')

    headers_and_content_indices = {tag: 0 for tag in tag_list}

    tag_iterator = html.find_all(tag_list)
    prev_header = None

    def get_tag_type(name):
        if name == 'h1' or name == 'h2' or name == 'h3':
            return 'header'
        elif name == 'p':
            return 'paragraph'
        elif name == 'ul':
            return 'unordered_list'
        else:
            return None

    if tag_iterator:
        for tag in tag_iterator:
            tag_name = tag.name.lower()
            tag_text = tag.get_text().strip()
            tag_type = get_tag_type(tag_name)

            headers_and_content_indices[tag_name] += 1
            index = f"{tag_name}_{tag_type}_{headers_and_content_indices[tag_name]}"

            if tag_name == 'h1' or tag_name == 'h2':
                base_json_dict[index] = {}
                base_json_dict[index]["header"] = tag_text
                base_json_dict[index]["content"] = {}
                prev_header = index

            elif tag_name == 'h3' or tag_name == 'p':
                if prev_header:
                    base_json_dict[prev_header]["content"][index] = tag_text
                else:
                    base_json_dict[index] = tag_text

            elif tag_name == 'ul':
                li_list = tag.find_all('li')
                items = [li.get_text().strip() for li in li_list]
                if prev_header:
                    base_json_dict[prev_header]["content"][index] = items
                else:
                    base_json_dict[index] = items

    return base_json_dict

# FOR EXPERIMENTATION WITH OPENAI ASSISTANTS API
#
# from rag import count_tokens, TOKENIZER_MODEL
# def generate_combined_html(marker_path):
#     tokens = []
#     with open(marker_path, 'r') as markers:
#         marker_dict = dict(json.load(markers))

#     with tqdm(total=124) as pbar:
#         for key in marker_dict.keys():
#             output_filename = f"{HTML_DIR_PATH}{key}.html"
#             start_marker = marker_dict[key]["start"]
#             end_marker = marker_dict[key]["end"]
#             with open(output_filename, "w") as combined_html_file:
#                 total_tokens = 0
#                 appendable_content = ""
#                 toc_list = ""
#                 for i in range(end_marker - start_marker + 1):
#                     index = i + start_marker
#                     df_path = f"{HTML_DIR_PATH}{index}.html"
#                     with open(df_path, 'r', encoding='utf-8') as html_file:
#                         html_content = html_file.read()
#                         total_tokens += count_tokens(html_content, TOKENIZER_MODEL)
                    
#                     html_subheader = f'<div id="file{index}">'
#                     html_subcontent_soup = BeautifulSoup(html_content, 'html5lib')
#                     html_subcontent = str(html_subcontent_soup)
#                     html_subfooter = f'</div>'

#                     html_subtitle = html_subcontent_soup.find('title').text
#                     toc_list += str(BeautifulSoup(f'<li><a href="#file{index}">{html_subtitle}</a></li>', 'html5lib'))
#                     appendable_content += str(BeautifulSoup(html_subheader + html_subcontent + html_subfooter, 'html5lib'))
#                     pbar.update()
                
#                 tokens.append(total_tokens)
                
#                 toc = str(BeautifulSoup(f"<ul>{toc_list}</ul>", 'html5lib'))
#                 file_header = str(BeautifulSoup('<html><head><meta charset="utf-8"/><meta content="width=device-width, initial-scale=1" name="viewport"/></head><body><h1>Index</h1>', 'html5lib'))
#                 file_footer = str(BeautifulSoup('</body></html>', 'html5lib'))
#                 combined_file_content = file_header + toc + appendable_content + file_footer
#                 file_soup = BeautifulSoup(combined_file_content,'html5lib')
#                 combined_html_file.write(file_soup.prettify())

#     return tokens

##################################### Scraping Functions #####################################

def get_sublinks(url):
    sublinks = []
    for link in soup.find_all('a'):
        external = link.get('href')
        if external is not None:
            if external.startswith("/"): # formats "/athletics" as https://www.scu.edu/athletics
                external = BASE + external
            if external.startswith("."):
                external = BASE + external[1:]
            if external.startswith("https://") and external.startswith(url) and external not in sublinks and external != url:
                sublinks.append(external)
    
    with open(SUBLINKS_PATH, "a") as text_file:
        for link in sublinks:
            text_file.write(link)
            text_file.write("\n")
    return sublinks

def scrape_recursive(url, max_depth=4):
    global htmls_generated
    if max_depth == 0:
        return []
    make_soup(url)
    sublinks = get_sublinks(url)
    htmls_generated += 1
    raw_html = getHTML(soup)
    content = map_HTML_to_JSON(refactor_html())
    output = [{"url": url, "content": content, "sublinks": sublinks}]

    with tqdm(total=len(sublinks)) as pbar:
        for sublink in sublinks:
            sublink_data = scrape_recursive(sublink, max_depth - 1)
            output.extend(sublink_data)
            pbar.update()

    return output

##################################### Main Executable #####################################

def scrape(url):
    with open(SUBLINKS_PATH, 'w') as sub:
        sub.write("") 
    scraped_data = scrape_recursive(url=url, max_depth=4)
    json_str = json.dumps(scraped_data, indent=1)

    with open(DATAFILE_PATH, 'w') as of:
        of.write(json_str)

def main():
    global htmls_generated
    htmls_generated = 0
    scrape(URL)
        
if __name__== "__main__":
    main()
