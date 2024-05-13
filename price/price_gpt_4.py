import tiktoken
import typing
import openai

# OpenAI Official Pricing Guide: https://openai.com/pricing
# Documentation: https://platform.openai.com/docs/guides/text-generation/managing-tokens

MODEL_GPT_4 = "gpt-4o"
GPT_4_PMPT_PRICE = 0.005         # 0.005 / 1k tokens -> Input price
GPT_4_CMPL_PRICE = 0.015         # 0.015 / 1k tokens -> Output price
GPT_4_TOKEN_LIMIT = 128000
GPT_4_MAX_RESPONSE_TOKENS = 1000
SERVICE_PRICE = 0.003            # Discord server fee (Added by me)

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

# Get answer from the OpenAI API and calculates the fee for messages
# This function is from another class (discord bot) and CANNOT be used directly
async def getAnswer(self, user_message: str, input_model) -> typing.Tuple[str, int, int, float]:

        if input_model == MODEL_GPT_35:
            self.msgs_gpt_35.append({"role": "user", "content": user_message})
            prev_token_size = price.getTokenSizeFromMsgs(self.msgs_gpt_4, model = MODEL_GPT_35)

            while (prev_token_size + GPT_35_MAX_RESPONSE_TOKENS >= GPT_35_TOKEN_LIMIT):
                del self.msgs_gpt_35[1]
                prev_token_size = price.getTokenSizeFromMsgs(self.msgs_gpt_35)

        else:
            self.msgs_gpt_4.append({"role": "user", "content": user_message})
            prev_token_size = price.getTokenSizeFromMsgs(self.msgs_gpt_4)

            while (prev_token_size + GPT_4_MAX_RESPONSE_TOKENS >= GPT_4_TOKEN_LIMIT):
                del self.msgs_gpt_4[1]
                prev_token_size = price.getTokenSizeFromMsgs(self.msgs_gpt_4)

        res, pmpt_tokens, cmpl_tokens, prices = '', 0, 0, 0.0

        try:
            response = await openai.ChatCompletion.acreate(
                    model = input_model,
                    messages = self.msgs_gpt_35 if input_model == MODEL_GPT_35 else self.msgs_gpt_4,
                    temperature = 0.8,
                    max_tokens = GPT_35_MAX_RESPONSE_TOKENS if input_model == MODEL_GPT_35 else GPT_4_MAX_RESPONSE_TOKENS,
            )
            
            res = response['choices'][0]['message']['content'].strip()

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

        except openai.APIError as e:
            if 'timed out' in str(e):
                print('[ERROR] Request timed out')
            else:
                print(f'[ERROR] {e}')
            
            res = str(e)
        
        return (res, pmpt_tokens, cmpl_tokens, prices)
