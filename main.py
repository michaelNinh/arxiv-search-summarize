import os
import dateutil.parser
import requests
from bs4 import BeautifulSoup
import re
import openai
import datetime

openai.api_key = 'YOUR_API_KEY'
gpt_version = "gpt-3.5-turbo"

keywords = ['large language models', 'openai']
max_papers = 2  # max amount of papers to summarize

summary_prompt = 'Summarize the user input in 3 sentences using simple english'

# research should not be older than this date
oldest_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)

base_url = 'http://export.arxiv.org/api/query?'
start = 0
size = 50

papers = []

while True:
    query = ' OR '.join(f'ti:"{kw}"' for kw in keywords)
    url = f'{base_url}search_query={query}&start={start}&max_results={size}&sortBy=submittedDate&sortOrder=descending'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'xml')
    entries = soup.findAll('entry')

    if not entries:
        break

    for entry in entries:
        published = dateutil.parser.parse(entry.published.text)
        if published < oldest_date or len(papers) == max_papers:
            break

        title = re.sub(r'\W+', '_', entry.title.text)
        if os.path.exists(f'papers/{title}.txt'):
            # print('already found: ' + title)
            continue

        papers.append({
            'title': entry.title.text,
            'id': entry.id.text,
            'abstract': entry.summary.text,
            'published': published
        })

    if published < oldest_date or len(papers) == max_papers:
        break

    start += size

for paper in papers:
    print('creating abstract summary for ' + paper['title'])
    completion = openai.ChatCompletion.create(
        model=gpt_version,
        messages=[
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": paper['abstract']}
        ],
        temperature=0,
        max_tokens=200
    )
    summary = completion['choices'][0]['message']['content']
    print('complete')

    # Save the summary to a text file
    title = re.sub(r'\W+', '_', paper['title'])
    with open(f'papers/{title}.txt', 'w') as f:
        f.write(f"Title: {paper['title']}\n")
        f.write(f"URL: {paper['id']}\n")
        f.write(f"Summary: {summary}\n")

    # Save the summary in the papers dictionary
    paper['summary'] = summary

# Print the abstract titles and summaries
print("\n" + "====" * 5 + " (*￣▽￣)b" + "\n")
for i, paper in enumerate(papers, 1):
    print(f'{i}. {paper["title"]}\n   {paper["summary"]}\n')


# Placeholder function for full summary
def full_summary(paper):
    # doing later
    return "oops! full summary feature isn't ready yet. check again later (っ˘ω˘ς )"
    # return paper['abstract']


# Allow the user to select papers to fully summarize
while True:
    try:
        selection = input("Enter paper numbers to summarize, separated by spaces like so 1 2 3, or 'q' to quit: ")
        if selection.lower() == 'q':
            break
        numbers = map(int, selection.split())
        for number in numbers:
            print(full_summary(papers[number - 1]))
    except (ValueError, IndexError):
        print("Invalid selection, please try again.")
