import tiktoken
import typing
import openai

# OpenAI Official Pricing Guide: https://openai.com/pricing
# Documentation: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions#managing-conversations

MODEL_GPT_35 = "gpt-3.5-turbo"
GPT_35_PRICE = 0.002            # 0.002 / 1k tokens -> Input tokens + Output tokens price

MODEL_GPT_4 = "gpt-4"
GPT_4_PMPT_PRICE = 0.03         # 0.03 / 1k tokens -> Input price
GPT_4_CMPL_PRICE = 0.06         # 0.06 / 1k tokens -> Output price

SERVICE_PRICE = 0.03            # Discord server fee (Added by me)

GPT_35_TOKEN_LIMIT = 4096
GPT_35_MAX_RESPONSE_TOKENS = 250

GPT_4_TOKEN_LIMIT = 8000
GPT_4_MAX_RESPONSE_TOKENS = 550

# Given a message list, returns the total token size of the messages
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

# *THIS IS A CLASS METHOD*
# Calls the ChatGPT API. Returns a tuple -> (API response string, prompt tokens, completion tokens, price)
async def getAnswer(self, user_message: str, input_model) -> typing.Tuple[str, int, int, float]:

    # Different language models use different arrays to store the conversation
    if input_model == MODEL_GPT_35:
        self.msgs_gpt_35.append({"role": "user", "content": user_message})
        prev_token_size = price.getTokenSizeFromMsgs(self.msgs_gpt_4, model = MODEL_GPT_35)

        # Prevent max token error
        while (prev_token_size + GPT_35_MAX_RESPONSE_TOKENS >= GPT_35_TOKEN_LIMIT):
            del self.msgs_gpt_35[1]
            prev_token_size = price.getTokenSizeFromMsgs(self.msgs_gpt_35)

    else:
        self.msgs_gpt_4.append({"role": "user", "content": user_message})
        prev_token_size = price.getTokenSizeFromMsgs(self.msgs_gpt_4)

        # Prevent max token error
        while (prev_token_size + GPT_4_MAX_RESPONSE_TOKENS >= GPT_4_TOKEN_LIMIT):
            del self.msgs_gpt_4[1]
            prev_token_size = price.getTokenSizeFromMsgs(self.msgs_gpt_4)

    res, pmpt_tokens, cmpl_tokens, prices = '', 0, 0, 0.0
    try:
        # ChatGPT API request (blocking)
        response = await openai.ChatCompletion.acreate(
                model = input_model,
                messages = self.msgs_gpt_35 if input_model == MODEL_GPT_35 else self.msgs_gpt_4,
                temperature = 0.8,
                max_tokens = GPT_35_MAX_RESPONSE_TOKENS if input_model == MODEL_GPT_35 else GPT_4_MAX_RESPONSE_TOKENS,
        )
        
        # Extract reply string
        res = response['choices'][0]['message']['content'].strip()

        # Price algorithm
        if input_model == MODEL_GPT_35:
            self.gpt_35_pmpt_tokens = response['usage']['prompt_tokens']
            self.gpt_35_cmpl_tokens = response['usage']['completion_tokens']
            tokens = self.gpt_35_pmpt_tokens + self.gpt_35_cmpl_tokens
            prices = tokens / 1000 * price.GPT_35_PRICE + price.SERVICE_PRICE

            self.msgs_gpt_35.append({"role": "assistant", "content" : res})
        else:
            self.gpt_4_pmpt_tokens = response['usage']['prompt_tokens']
            self.gpt_4_cmpl_tokens = response['usage']['completion_tokens']
            prices = \
                self.gpt_4_pmpt_tokens / 1000 * price.GPT_4_PMPT_PRICE + \
                self.gpt_4_cmpl_tokens / 1000 * price.GPT_4_CMPL_PRICE + \
                price.SERVICE_PRICE

            self.msgs_gpt_4.append({"role": "assistant", "content" : res})
        
        pmpt_tokens = self.gpt_35_pmpt_tokens if input_model == MODEL_GPT_35 else self.gpt_4_pmpt_tokens
        cmpl_tokens = self.gpt_35_cmpl_tokens if input_model == MODEL_GPT_35 else self.gpt_4_cmpl_tokens

        print(f'ChatGPT: {res}')

    except openai.error.APIError as e:
        if 'timed out' in str(e):
            print('[ERROR] Request timed out')
        else:
            print(f'[ERROR] {e}')
        
        res = str(e)
    
    return (res, pmpt_tokens, cmpl_tokens, prices)