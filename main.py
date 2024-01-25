import openai
import os


def run():
    print(os.environ.get("OPENAI_API_KEY"))
    print(os.environ)
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a tutor, skilled in explaining writing concepts in a way that someone who has never seen the concept before will understand."},
            {"role": "user",
             "content": "Explain to me how to write a thesis statement."}
        ]
    )

    print(completion.choices[0].message)


if __name__ == "__main__":
    run()
