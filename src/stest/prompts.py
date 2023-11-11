# This prompt is used to contextualize the task that CHAT-GPT will have to perform.
# It is used by the create_tests command to produce tests for all the files that are
# being tracked by stest.
# 
# It is the initial_prompt (check openai_iface.py/send_data_in_chunks_and_get_response)
# which will be the task Chat GPT will have to perform after all the data is sent.
CREATE_TESTS_PROMPT = """
    You are an experienced software developer who has been hired to
    write unit tests. You will be given a set of files and your job
    is to write EXTENSIVE unit tests for them. The files are written in {language}
    and the tests MUST be written using {test_framework}.

    I will now give you a set of files, where the content of each file is
    the code that you will have to write tests for. The files will be separated
    by the delimiter 'FILE STARTS HERE'; the line that follows the delimiter will
    be the name of the file.
    When I am finished, I will tell you 'ALL FILES SENT'.

    DO NOT answer until you have received all the files.

    In the end, you will return the code for the tests that you have written using
    the same delimiter '= FILE STARTS HERE ='. The line that follows the delimiter
    must be the name of the file that the tests are for (the original name + the "test_" prefix).

    You MUST ONLY return the code for the tests that you have written. NOTHING ELSE.
    The code MUST NOT INCLUDE MARKDOWN SYNTAX.

    The file name must be all lowercase and must not contain any spaces.
    DO NOT RETURN ANYTHING BUT THE CODE.
"""

# This prompt is used to check if the given file is written 
# in the given language.
#
# It is the initial_prompt (check openai_iface.py/send_data_in_chunks_and_get_response)
# which will be the task Chat GPT will have to perform after all the data is sent.
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

SEND_FILES_PROMPT = """
    To provide the context for the above prompt, I will send you the content of all the files in parts.
    When I am finished, I will tell you 'ALL FILES SENT'.
"""

# This prompt informs CHAT-GPT that the file has been fully sent.
ALL_PARTS_SENT_PROMPT = "ALL PARTS SENT"

# This prompt informs CHAT-GPT that all the files have been fully sent.
ALL_FILES_SENT_PROMPT = "ALL FILES SENT"


