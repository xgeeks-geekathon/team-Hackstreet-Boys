CONTEXT_PROMPT = """
    You are an experienced software developer who has been hired to
    write unit tests. You will be given a set of files and your job
    is to write unit tests for them. The files are written in {language}
    and the tests MUST be written using {test_framework}.

    I will now give you a set of files, where the content of each file is
    contained between these two lines: {start_delimiter} and {end_delimiter}.
    
    The files will be fed in chunks using the following format:
    <file_name>
    <start_delimiter>
    <file_content>
    <end_delimiter>

    In the end, after all files have been fed, 
"""

FEED_FILE_PROMPT = """
    {file_name}
    {start_delimiter}
    {file_content}
    {end_delimiter}
"""

# This prompt is used to check if the given file is written 
# in the given language.
CHECK_FILE_LANGUAGE_PROMPT = """
    I will give you a file and you will have to tell me if the file is written in {language}.
    When I am finished, I will tell you 'FILE FULLY SENT'.
    DO NOT answer until you have received the whole file.
    In the end, after the file as been fed, return ONLY "Yes" or "No".
"""

SEND_FILE_PROMPT = """
    To provide the context for the above prompt, I will send you the file content in parts. 
    When I am finished, I will tell you 'ALL PARTS SENT'. 
    DO NOT answer until you have received all the parts.
"""

# This prompt informs CHAT-GPT that the file has been fully sent.
ALL_PARTS_SENT_PROMPT = "ALL PARTS SENT"
