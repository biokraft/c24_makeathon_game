import tiktoken

def check_token_limit(message: str, limit: int = 4096, encoding_name: str = "cl100k_base") -> bool:
    """
    Check if the token count of a message is within the limit.

    Args:
		message (str): The message to check.
		limit (int): The token limit.
		encoding_name (str): The encoding name to use.

	Returns:
		bool: True if the token count is within the limit, False otherwise.
    """
    encoding = tiktoken.get_encoding(encoding_name=encoding_name)
    return len(encoding.encode(message)) <= limit
