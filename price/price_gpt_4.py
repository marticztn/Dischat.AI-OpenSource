import tiktoken

# OpenAI Official Pricing Guide: https://openai.com/pricing
# Documentation: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions#managing-conversations

MODEL_GPT_35 = "gpt-3.5-turbo"
GPT_35_PRICE = 0.002            # 0.002 / 1k tokens -> Input tokens + Output tokens price

MODEL_GPT_4 = "gpt-4"
GPT_4_PMPT_PRICE = 0.03         # 0.03 / 1k tokens -> Input price
GPT_4_CMPL_PRICE = 0.06         # 0.06 / 1k tokens -> Output price

SERVICE_PRICE = 0.03            # Discord server fee (Added by me)

def getTokenSizeFromMsgs(msgs: list, model = MODEL_GPT_4) -> int:
    # Use GPT-4 encoding
    token_size = 0
    encoding = tiktoken.encoding_for_model(MODEL_GPT_4)

    for msg in msgs:
        # Every message has a 'role' and a 'content' field, which is 4 tokens
        token_size += 4
        for key, val in msg.items():
            token_size += len(encoding.encode(val))

    # Every API response(output / sample / reply) is primed with an 'assistant' field behind the scenes
    token_size += 2
    return token_size