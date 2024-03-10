import openai
from app.scrape import rag
import time

TEXTGEN_MODEL = "gpt-3.5-turbo"

openai_client = openai.OpenAI(api_key="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")

def openai_pass_prompt(query):
    context = rag.generate_sections(query=query, num_sections=5)
    request = [
        {'role' : 'system', 'content' : "You are a specialized assistant designed for students at Santa Clara University (SCU), focusing on offering targeted guidance and information drawn from SCU's online resources. Students approach with varied inquiries related to course selection, including details on prerequisites, instructor evaluations, course descriptions, and scheduling options. They often need assistance navigating SCU's comprehensive web materials to find specific information. Your role involves: 1. Analyzing User Queries: Understand the specific nature of each student's query, considering their academic interests, career objectives, and personal preferences. 2. Identifying Relevant Information: Examine the sections provided below to determine which one most closely aligns with the user's needs. 3. Summarizing Key Details: From the most pertinent section, extract and summarize essential information that addresses the student's question effectively. 4. Tailoring Recommendations: Offer personalized advice based on the information found, aligning with the student's academic and career goals. 5. Providing Clear Responses: Deliver your answers in a clear, comprehensive manner. Include the URL(s) for referenced sources to allow students to explore further. 6. Encouraging Interaction: Invite additional questions to clarify any uncertainties and ensure the student feels supported and understood. 7. Soliciting Feedback: Ask for the student's feedback to refine and enhance future interactions. Given the user's message below, fulfill your role by adhering to these guidelines and assist the student by leveraging the relevant section's content to provide a well-rounded answer."},
        {'role' : 'user', 'content' : "User's message: " + query},
        {'role' : 'user', 'content' : context},
    ]

    # begin_call = time.time()
    # response = openai_client.chat.completions.create(
    #     model=TEXTGEN_MODEL,
    #     messages=request,
    #     temperature=0.1,
    #     max_tokens=1100,
    # ).choices[0].message.content
    # end_call = time.time()
    # print("\nInitial OpenAI call took {:.2f} seconds to execute.\n".format(end_call - begin_call))

    # return response
    return request

def main():
    # query = "Tell me about COEN 140 and COEN 163"
    # response = openai_pass_prompt(query=query)
    # print(response)
    print("hello world")

if __name__ == "__main__":
    main()