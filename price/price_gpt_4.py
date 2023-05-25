# Documentation: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions#managing-conversations

import tiktoken

MODEL = 'gpt-4-0314'
PROMPT_PRICE = 0.03     # 0.03 / 1k tokens -> Input price
CMPL_PRICE = 0.06       # 0.06 / 1k tokens -> Output price
SERVICE_PRICE = 0.05    # Discord server fee (Added by me)
encoding = tiktoken.encoding_for_model(MODEL)

def getTokenSizeAndPriceFromMsg(input: str, output: str) -> tuple:
    global encoding

    # Every message has a 'role' and a 'content' field, which is 4 tokens
    total_tokens = 4

    # Calculate the number of tokens used by the prompt and the reply from ChatGPT
    input_tokens = len(encoding.encode(input))
    output_tokens = len(encoding.encode(output))
    total_tokens += input_tokens + output_tokens
    
    # Every API response(output / reply) is primed with an 'assistant' field behind the scenes
    total_tokens += 2

    # Calculate the price for each conversation
    input_price = PROMPT_PRICE * (input_tokens / 1000)
    output_price = CMPL_PRICE * (output_tokens / 1000)
    total_price = input_price + output_price + SERVICE_PRICE

    return (total_tokens, total_price)