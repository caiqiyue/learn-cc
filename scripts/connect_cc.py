import anthropic

client = anthropic.Anthropic(
    api_key='sk-api-pwz3WAu6O1KI109JMrhup72vSu8r3NrFN5P-4pTcs57bLDHtOaYr5ndVP3eWTEQ8UxKNcF75dCPI9B5RtIjOXYxg8cfDXd-2mFnqcITBov0bB-mQoPEpPpI',
    base_url='https://api.minimaxi.com/anthropic'

)

message = client.messages.create(
    model="MiniMax-M2.5",
    max_tokens=1000,
    system="You are a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hi, how are you?"
                }
            ]
        }
    ]
)

for block in message.content:
    if block.type == "thinking":
        print(f"Thinking:\n{block.thinking}\n")
    elif block.type == "text":
        print(f"Text:\n{block.text}\n")