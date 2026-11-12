# [2024] Outokumpu — Sustainable generative AI assistant for insights

## Metadata

- **Year**: 2024
- **Challenge Partner**: Outokumpu
- **Original Historical Track**: Sustainability
- **2026 Target Track**: AI Infrastructure Track (by Verda)
- **Sub-theme**: IV. Green Compute, Trustworthy Inference & Telemetry Infra
- **Core Theme**: Pluggable Model Architecture, Energy-Efficient Inference Optimization for Small Models, and Query-Level Energy/Carbon Estimation
- **Classification Rationale**: Derived from the Sustainability track, it explicitly requires designing a lightweight architecture with hot-swappable (interchangeable) model components rather than relying on brute-force stacking of ultra-large models and ultra-long contexts, and quantitatively estimating the inference compute and energy cost per LLM query, perfectly aligning with Verda's green and efficient AI infrastructure philosophy.

---

## Full Original Challenge Name

Sustainable generative AI assistant for insights

## Challenge Description

Your challenge, should you accept it, is to build a sustainable AI assistant for dynamic information retrieval and summarization to support business critical use cases. As Sustainable AI is a very broad topic, to keep things simple, for this challenge we would like to focus on two aspects of Sustainable AI: trustworthiness and efficiency (which we are using here as a proxy for ecological sustainability, through more limited energy use and carbon footprints). So this is not “just” about building an information retrieval assistant and feeding huge amounts of data to an enormous model – that is easy. We want you to build a system that accomplishes the same but in a very trustworthy and sustainable way, and that makes things quite a bit more challenging… so you need to work smart not just hard on how you accomplish the task, as “bruteforcing” this will not result in the desired outcome. But hey, that’s why this is called a challenge, we know you are up for it!\
\
Trustworthiness has also a few different aspects. Firstly, it is about using the right data – as correct information as possible as the source. We all know that the internet is not necessarily always correct… so how do you know what sources to trust? But even when you have the right information, summarizing that might not always get you what you want either. One of the fairly common challenges of generative models is hallucinations, effectively inventing results to questions where there are none. This leads to a lack of trust and can even be a barrier to usage. You should strive to build a system that bases the outputs on sources you can trust and avoids hallucinations to ensure the outputs of the system are reliable and trustworthy.\
\
Furthermore, as we know, large language models are quite resource intensive. Especially training models tends to consume large amounts of energy, but also interference (when you use the models) can be costly – especially when done at scale. As it is not in scope for this challenge to build a model from scratch, let’s focus on the computational costs related to using an existing model – both in terms of which model to choose and how we use it. This is something we can often control better in practical applications too, as even if we use existing large models, we can definitely decide which ones to use and how we use them. So while this is a very exciting set of technologies, we should use them wisely and avoid excessive resource consumption. Less is definitely more in this context – and the best solution probably does not use the biggest model or the broadest context possible (or very large amounts of queries to a model – it is the total cost that counts) – and a big part of the challenge is to optimize the resource usage while still getting great results.\
\
This solution, if successful, can make a huge difference – and shed light on how tasks like can be accomplished in a sustainable way. So it is not just about building something very cool and useful but showcasing how thinking about of the sustainability of AI can make a real positive difference!\
\

## Challenge Insights

As to the actual solution, we will encounter different types of questions, and ideally the solution could have quite general applicability. But since that is of course rather complex to construct, let’s focus on some example questions (note – these are not the only questions the solution should answer, just some examples to give you an idea – when evaluating your solution, we will use similar but not necessarily just these):\
\
1. What is the expected development of stainless steel market pricing for a specific alloy in the next month?\
\
2. What recent news state about possible energy price developments over the next three months?\
\
3. What are the most recent patents granted in the area of stainless steel manufacturing?\
\
For practicality, we expect the assistant to be able to connect to the internet, fetch relevant data and be able to produce well summarized results in human readable format in the range of one or two paragraphs per question – with a special focus on avoiding hallucinations and basing the results on the source information and being ecological and efficient in how this is done. The results should always include a reference to the sources of the information used to construct the answer.\
\
The architecture should be such that the actual model component is easily interchangeable (as this is a rapidly developing field), and working from the assumption that you do not need to fine-tune or retrain the actual model, but supply the data through prompting in a way that you find most effective. And in order to evaluate your ecological consumption, we would like you to also estimate the energy impact of the query having been executed (understanding that this is just an estimate, and using the number and size of queries and size of the model used as proxy is a good approach – although we welcome you to innovate also in this front)\

## Judging Criteria

The selection of the winner will be a combination of subjective evaluation of the technical implementation and quality of outputs by the Outokumpu team. The key evaluation dimensions used for scoring the solutions are:\
\
1. Trustworthiness of results – hallucinations impede the needed trust and must be avoided, and sources that are reliable should be emphasized. One part of this is providing the references, but also making sure that the answer is based on real facts and is as correct as possible.\
\
2. Efficiency of the solution – ideally the amount of calculations, queries and consequently energy consumption should be optimized for efficiency and ecological impact. This means that in order to get the best score from the evaluation, you should pay close attention to what model you use and how. It might be easiest to get nice results just by calling for example one of OpenAI’s larger LLMs, but due to the size of the models, their efficiency is probably not the best – especially if you perform multiple queries with big context sizes. Using a smaller model and constructing your queries in a smart way can go a long way towards more efficient solutions.\
 \
3. Comprehensiveness and readability of the results – summarizations must be comprehensive but still easy to understand, and provide references to source data in a usable manner. Ideal length of a response is a 1-2 paragraphs, but this naturally depends on the question. Simple and concise is the goal.\
\
4. Architecture choices – you should strive towards a structure that allows for interchangeability of parts of the solutions should new approaches, for example more ecological language models, emerge. \
\
Please note that the expectation here is not to train your own LLM – that would also be very resource and energy consuming – but emphasize what model you choose to use and how you use it to be able to produce high quality trustworthy results in an efficient manner. And of course, if you have any questions, please reach out to the Outokumpu team – we are more than happy to answer any questions!\

## Prizes

Winning team will get 2000€, the first runner up 1000€ and the second runner up 500€.

## Resources

We will have people onsite to answer questions (detailed hours to be communicated later) and ability to reach out for questions via asynchronous means (email or other digital channels). We will also be available for meetings to discuss and answer questions.\
