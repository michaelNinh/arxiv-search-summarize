import os
import dateutil.parser
import requests
import re
import openai
import datetime
from bs4 import BeautifulSoup
from pdf import pdf_to_text, create_chunks, abs_to_pdf
import tiktoken
from dotenv import load_dotenv


load_dotenv()  # take environment variables from .env.

openai.api_key = os.getenv("SECRET_KEY")
gpt_version = "gpt-3.5-turbo"

keywords = ['large language models', 'openai']
max_papers = 1  # max amount of papers to summarize

summary_prompt = 'Summarize the user input in 3 sentences using simple english'
full_summary_prompt = 'The following user input is an excerpt from a research paper. Produce a short-length summary of ' \
                      'the text using simple English. If there is text not related to the research, ' \
                      'such as references, do not include it in the summary.'

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


def full_summary(paper):
    def summarize_chunks(chunks):
        all_summaries = []
        print("# Chunks: " + str(len(chunks)))
        round = 0
        for chunk in chunks:
            print("summarizing chunk: " + str(round + 1))
            completion = openai.ChatCompletion.create(
                model=gpt_version,
                messages=[
                    {"role": "system", "content": full_summary_prompt},
                    {"role": "user", "content": chunk}
                ],
                temperature=0,
                max_tokens=200
            )
            chunk_summary = completion['choices'][0]['message']['content']
            all_summaries.append(chunk_summary)
            round += 1

        if len(chunks) > 1:
            # If there's more than one chunk, summarize the combined summaries
            return summarize_chunks([' '.join(all_summaries)])
        else:
            # If there's only one chunk left, return its summary
            return all_summaries[0]

    pdf_url = abs_to_pdf(paper['id'])
    pdf_text = pdf_to_text(pdf_url)
    chunk_size = 1750
    overlap = 100
    chunks = create_chunks(pdf_text, chunk_size, overlap)

    # Check token count for each chunk and decrease chunk size if necessary
    for chunk in chunks:
        encoding = tiktoken.encoding_for_model(gpt_version)
        token_count = len(encoding.encode(chunk)) + len(encoding.encode(full_summary_prompt))
        while int(token_count) > 4096:
            chunk_size = int(chunk_size * 0.9)
            overlap = int(overlap * 0.9)
            chunks = create_chunks(pdf_text, chunk_size, overlap)
            token_count = encoding.encode(chunk) + encoding.encode(full_summary_prompt)
    final_summary = summarize_chunks(chunks)
    title = re.sub(r'\W+', '_', paper['title'])
    with open(f'papers/{title}.txt', 'a') as f:
        f.write(f"Final Summary: {final_summary}\n")
    paper['final_summary'] = final_summary
    print("====FULL SUMMARY====")
    return final_summary

# Allow the user to select papers to fully summarize
summarized_papers = set()

while True:
    try:
        selection = input("Enter paper numbers to summarize, separated by spaces like so '1 2 3', or 'q' to quit: ").strip()
        if selection.lower() == 'q':
            break
        numbers = map(int, selection.split())
        for number in numbers:
            if number not in summarized_papers:  # Check if the paper is already summarized
                print(full_summary(papers[number - 1]))
                summarized_papers.add(number)  # Add the number to the set of summarized papers
        # Check if all papers have been summarized
        if len(summarized_papers) == len(papers):
            print("All papers have been summarized.")
            break
    except (ValueError, IndexError):
        print("Invalid selection, please try again.")
