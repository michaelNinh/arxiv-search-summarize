**ARXIV QUERY & SUMMARIZE**

A simple python script that keyword searches papers and summarizes the abstract in simple English using OpenAI's chatGPT API. Research for everyone!

Feel free to customize / PR.

**Installation:**
```
#add your api key
pip install -r requirements.txt 
python main.py
```

**Bugs:**
- Selecting multiple papers to summarize will sometimes fail

**Features:**
- first summarizes paper abstract to help you make a decision if you want the full summary
- summarizes the entire paper if selected
- select GPT version
- use your own summary prompt
- add your own tags
- saves papers as txt 
- ignores already saved papers
- runs in console, prints summaries in console 

**To do later:**
- add costs
- retry on fail & better error handling
- search for new  papers added since list time the script ran

**Example output:**

papers/Fast_Distributed_Inference_Serving_for_Large_Language_Models.txt/

Title: Fast Distributed Inference Serving for Large Language Models

URL: http://arxiv.org/abs/2305.05920v1

Summary: FastServe is a new system that helps large language models (LLMs) to work faster and more efficiently. It uses a special scheduling method that allows it to complete tasks more quickly by breaking them down into smaller parts. This means that it can handle more tasks at once and complete them faster than other systems. FastServe also has a special memory management system that helps it to work more efficiently with LLMs.
