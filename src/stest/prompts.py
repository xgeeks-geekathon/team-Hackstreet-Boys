

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

    In the end, 

"""

FEED_FILE_PROMPT = """
    {file_name}
    {start_delimiter}
    {file_content}
    {end_delimiter}
"""

CHECK_FILE_LANGUAGE_PROMPT = """
    
"""
