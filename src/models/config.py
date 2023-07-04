from enum import Enum
import os
import logging
import random


from pydantic import HttpUrl, parse_obj_as


class LLMType(str, Enum):
    openai = "openai"

    @classmethod
    def is_in_members(cls, value: str) -> bool:
        return value in cls._member_names_


class RunEnv(str, Enum):
    dev = "dev"
    prod = "prod"


class ModelType(str, Enum):
    openai_gpt35 = "gpt-3.5-turbo"
    openai_gpt35_16 = "gpt-3.5-turbo-16k"
    openai_gpt4 = "gpt-4-0613"
    openai_text_davinci = "text-davinci-003"

    @classmethod
    def openai_chat_default(cls):
        return cls.openai_gpt35_16


class Config:
    # read env variables
    llm_host = os.environ.get('LLM_HOST', 'https://api.openai.com')
    llm_tokens = os.environ.get('LLM_TOKENS', '').split(',')
    llm_type = os.environ.get('LLM_TYPE', 'openai')
    env = os.environ.get('ENV', 'dev')

    def __init__(self):
        pass

    @classmethod
    def config_check(cls) -> bool:
        # check llm_type
        if not LLMType.is_in_members(cls.llm_type):
            logging.error("LLM_TYPE is not valid")
            return False

        # check llm_tokens
        if cls.llm_type == LLMType.openai and len(cls.llm_tokens) == 1 and cls.llm_tokens[0] == '':
            logging.error("LLM_TOKENS is not set")
            return False
        # check llm_host is url
        if not cls.llm_host.startswith('http'):
            logging.error("LLM_HOST is not url")
            return False
        return True

    def get_token(self) -> str | None:
        # if len of llm_token bigger than 1, random choice one
        if len(self.llm_tokens) > 1:
            return random.choice(self.llm_tokens)
        elif len(self.llm_tokens) == 0:
            return None
        else:
            return self.llm_tokens[0]

    def get_base_url(self) -> HttpUrl:
        return parse_obj_as(HttpUrl, self.llm_host)

    def get_llm_type(self) -> LLMType:
        return LLMType(self.llm_type)

    @classmethod
    def is_dev(cls) -> bool:
        return cls.env == RunEnv.dev

    @classmethod
    def is_prod(cls) -> bool:
        return cls.env == RunEnv.prod