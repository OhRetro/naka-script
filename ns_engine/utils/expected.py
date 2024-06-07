from string import ascii_letters
from ..components.token import TokenType
from ..components.keyword import Keyword

def expected(*token_type_or_keyword: TokenType | Keyword):
    error_message_str = "Expected "
    expected_items = token_type_or_keyword
    
    if not expected_items:
        return error_message_str + "a list with something at least, This is not a Nakathon error"

    if len(expected_items) == 1:
        exp_value = expected_items[0].value
        if isinstance(expected_items[0], Keyword) or exp_value[0] not in ascii_letters:
            error_message_str += f"'{exp_value}'"
        else:
            error_message_str += f"{exp_value}"
    else:
        for i, item in enumerate(expected_items[:-2]):
            if isinstance(item, (TokenType, Keyword)):
                exp_value = item.value
                if isinstance(item, Keyword) or exp_value[0] not in ascii_letters:
                    error_message_str += f"'{exp_value}', "
                else:
                    error_message_str += f"{exp_value}, "
            else:
                return error_message_str + "a list with only TokenType or Keyword, This is not a Nakathon error"

        second_last = expected_items[-2]
        last = expected_items[-1]
        
        if isinstance(second_last, (TokenType, Keyword)):
            exp_value = second_last.value
            if isinstance(second_last, Keyword) or exp_value[0] not in ascii_letters:
                error_message_str += f"'{exp_value}' or "
            else:
                error_message_str += f"{exp_value} or "
        else:
            return error_message_str + "a list with only TokenType or Keyword, This is not a Nakathon error"

        if isinstance(last, (TokenType, Keyword)):
            exp_value = last.value
            if isinstance(last, Keyword) or exp_value[0] not in ascii_letters:
                error_message_str += f"'{exp_value}'"
            else:
                error_message_str += f"{exp_value}"
        else:
            return error_message_str + "a list with only TokenType or Keyword, This is not a Nakathon error"

    return error_message_str
