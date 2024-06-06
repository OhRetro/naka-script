from string import ascii_letters
from ..components.token import TokenType
from ..components.keyword import Keyword

def expected(*token_type_or_keyword: TokenType | Keyword):
    error_message_str = "Expected "
    expected_chars = token_type_or_keyword
    
    if len(expected_chars) == 1:
        exp_value = expected_chars[0].value
        error_message_str += f"'{exp_value}'" if exp_value[0] not in ascii_letters else f"{exp_value}"

    elif len(expected_chars) > 1:
        for i in expected_chars:        
            if isinstance(i, TokenType) or isinstance(i, Keyword):
                if i != expected_chars[-1] and i != expected_chars[-2]:
                    exp_value = i.value
                    error_message_str += f"'{exp_value}', " if exp_value[0] not in ascii_letters else f"{exp_value}, "
                else:
                    break
            else:
                error_message_str += "a list with only TokenType or Keyword, This is not an Nakathon error"
                return error_message_str
            
        exp_value = expected_chars[-2].value
        error_message_str += f"'{exp_value}' or " if exp_value[0] not in ascii_letters else f"{exp_value} or "
        exp_value = expected_chars[-1].value
        error_message_str += f"'{exp_value}'" if exp_value[0] not in ascii_letters else f"{exp_value}"
    
    else:
        error_message_str += "a list with something at least, This is not an Nakathon error"
    
    return error_message_str
