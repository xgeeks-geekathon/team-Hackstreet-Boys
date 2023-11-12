########################################################################
# @file stest.py                                                       #
# @brief Stest Core Module                                             #
#                                                                      #
# This module contains the core functionality of stest.                #            
# It is responsible for initializing the stest environment,            #
# adding and removing files, creating tests, and showing               #
# the status of the stest environment as well as other                 #
# functionalities.                                                     #
#                                                                      #
# @date 2023-11-12                                                     #
#                                                                      #
# @authors                                                             #
#   - https://www.github.com/joaoajmatos                               #
#   - https://www.github.com/joaooliveira1201                          #
#   - https://www.github.com/freaktsg                                  #
#                                                                      #
########################################################################

import json
import os
import re

from colorama import Fore, Style

# Local imports
from . import utils
from .openai_iface import IOpenAI
from . import prompts

########################################################################

# List of supported testing frameworks
# for each language
TESTING_FRAMEWORKS = {
    "c": "criterion",
    "cpp": "criterion",
    "py": "pytest",
    "js": "jest"
}

# Default stest config
DEFAULT_CONFIG = {
    "tracked_files": {},
    "language": "",
    "test_framework": "",
    "test_command": "",
}

# Dir name for stest environments
STEST_DIR = ".stest"
STEST_CONFIG_FILE = "config.json"

DIR_SEPARATOR = "\\"
if utils.is_posix():
    DIR_SEPARATOR = "/"

FILE_START_DELIMITER = "= FILE STARTS HERE ="
PREV_TEST_FILE_START_DELIMITER = "= PREVIOUS TEST FILE STARTS HERE ="

# This is the maximum depth of parent directories that will be searched
# for a stest environment. This is so that the user can run stest from
# a subdirectory of the stest environment, just like in git.
MAX_PARENT_SEARCH_DEPTH = 5

########################################################################

class Stest:
    def __init__(self):
        self.config = None
        self.openai_iface = IOpenAI()

        self.stest_environment_root = self.__fetch_stest_environment_root()

    ###############################
    # Public methods              #
    ###############################

    # @brief Initializes a new stest environment
    # @param path Path to the stest environment
    def init(self, path: str, test_dir: str, language: str) -> None:
        if self.stest_environment_root != None:
            raise Exception("The current directory/workspace already contains a stest environment.")

        utils.create_dir(path + DIR_SEPARATOR + STEST_DIR)
        config_file_path = path + DIR_SEPARATOR + STEST_DIR + DIR_SEPARATOR + STEST_CONFIG_FILE
        self.__create_config_file(config_file_path, test_dir, language)
        self.__load_config_file(config_file_path)
        print("Initialized empty stest environment.")


    # @brief Adds a list of files to the tracked files
    # @param paths List of paths to the files 
    def add(self, paths: list[str]) -> None:
        if self.stest_environment_root == None:
            raise Exception("The current directory/workspace is not a stest environment.")

        self.__load_config_file(self.stest_environment_root + DIR_SEPARATOR + STEST_CONFIG_FILE)

        print("Please wait while stest checks the file(s)...")

        for path in paths:
            path = utils.relative_path_to_absolute_path(path)

            if not os.path.exists(path):
                raise Exception(f"No such file or directory: {path}")
            elif utils.is_dir(path):
                self.__track_all_files_in_directory(path)
            elif self.__file_is_tracked(path):
                raise Exception(f"The file {path} is already being tracked. Use 'stest remove' to stop tracking the file.")
            else:
                self.__track_file(path)

        # We dont need to save config here bc __track_file does it for us


    # @brief Removes a list of files from the tracked files
    # @param paths List of paths to the files
    def remove(self, paths: list[str]) -> None:
        if self.stest_environment_root == None:
            raise Exception("The current directory/workspace is not a stest environment.")

        self.__load_config_file(self.stest_environment_root + DIR_SEPARATOR + STEST_CONFIG_FILE)

        for path in paths:
            path = utils.relative_path_to_absolute_path(path)

            if not os.path.exists(path):
                raise Exception(f"No such file or directory: {path}")
            elif utils.is_dir(path):
                self.__untrack_all_files_in_directory(path)
            elif not self.__file_is_tracked(path):
                raise Exception(f"The file/directory {path} is not being tracked. Use 'stest add' to start tracking the file.")
            else:
                self.__untrack_file(path)

        self.__save_config_file(self.stest_environment_root + DIR_SEPARATOR + STEST_CONFIG_FILE)
        print("Done.")


    # @brief Creates the tests for the tracked files
    def create_tests(self) -> None:
        if self.stest_environment_root == None:
            raise Exception("The current directory/workspace is not a stest environment.")

        self.__load_config_file(self.stest_environment_root + DIR_SEPARATOR + STEST_CONFIG_FILE)
        files_to_test = []
        previous_test_files = []

        for file in self.config["tracked_files"]:
            if self.__file_has_changed(file):
                if self.__file_has_previous_test_file(file):
                    previous_test_files.append(file)

                files_to_test.append(file)

        if len(files_to_test) == 0:
            print(f"{Fore.YELLOW}No modifications since last test generation were found, aborting.{Style.RESET_ALL}")
            return

        print(f"Generating tests for {len(files_to_test)} files. This may take a while.")
        
        data_to_send = ""
        for file in files_to_test:
            self.config["tracked_files"][file]["hash"] = utils.get_file_hash(file)
            data_to_send += self.__build_serialized_file_data(file)

        for file in previous_test_files:
            data_to_send += self.__build_serialized_previous_test_file_data(file)

        prompt_to_use = None
        if len(previous_test_files) > 0:
            print(f"{Fore.YELLOW}Previous test files were found for {len(previous_test_files)} file(s). Stest will refactor them.{Style.RESET_ALL}")
            prompt_to_use = prompts.CREATE_TESTS_REFACTOR_PROMPT
        else:
            prompt_to_use = prompts.CREATE_TESTS_PROMPT

        response = self.openai_iface.send_data_in_chunks_and_get_response(
            prompt_to_use, data_to_send
        )

        utils.create_dir(self.config["test_dir"])
        self.__save_serialized_test_data(self.config["test_dir"], response)
        self.__save_config_file(self.stest_environment_root + DIR_SEPARATOR + STEST_CONFIG_FILE)
        print(f"{Fore.GREEN}Tests have been written to {utils.absolute_path_to_relative_path(self.config['test_dir'])}.{Style.RESET_ALL}")

    
    # @brief Displays the current status of the stest environment
    #
    # @details This method displays the current status of the stest environment.
    #          It shows all the tracked files, and the ones that have been modified
    #          since the last test generation.
    #
    def status(self) -> None:
        if self.stest_environment_root == None:
            raise Exception("The current directory/workspace is not a stest environment.")

        self.__load_config_file(self.stest_environment_root + DIR_SEPARATOR + STEST_CONFIG_FILE)

        print(f"On workspace {Fore.LIGHTBLACK_EX}{utils.absolute_path_to_relative_path(self.stest_environment_root)}{Style.RESET_ALL}\n")
        print(f"Test directory: {Fore.LIGHTBLACK_EX}{utils.absolute_path_to_relative_path(self.config['test_dir'])}{Style.RESET_ALL}")
        print(f"Language: {Fore.LIGHTBLACK_EX}{self.config['language']}{Style.RESET_ALL}\n")

        if len(self.config["tracked_files"]) == 0:
            print(f"{Fore.YELLOW}No tracked files were found.{Style.RESET_ALL}")
            print(f"Use '{Fore.LIGHTBLACK_EX}stest add{Style.RESET_ALL}' to add files to the tracked files.")
            return

        print(f"Tracked files in current test environment ({Fore.LIGHTBLACK_EX}{len(self.config['tracked_files'])}{Style.RESET_ALL}):")
        for file in self.config["tracked_files"]:
            relative_path = utils.absolute_path_to_relative_path(file)
            if self.__file_has_changed(file):
                print(f"  {Fore.YELLOW}{relative_path} (modified){Style.RESET_ALL}")
            else:
                print(f"  {Fore.GREEN}{relative_path} {Style.RESET_ALL}")


    ###############################
    # Private methods             #
    ###############################

    # @brief Checks if a given test file exists in the test directory
    #
    # @details This method checks if a given test file exists in the test directory
    #          of the current stest environment. This is used in order to determine
    #          if the previous test implementation should be fed to the GPT-4 engine
    #          or not.
    #
    #          We do this because GPT-4 may create completely different tests for the
    #          same file. This would make for unnecessary refactoring of the tests and
    #          possibly even a completely different test logic.
    #
    #          Chat GPT will be asked to take into account the last test implementation
    #          if it exists, and try to stick to it as much as possible.
    #
    #          (check prompts.py/CREATE_TESTS_REFACTOR_PROMPT for more details)
    #
    # @param file Path to the file
    # @return True if the file exists, False otherwise
    def __file_has_previous_test_file(self, file: str) -> bool:
        filename = utils.get_filename(file)
        test_filename = "test_" + filename # TODO: Maybe make this configurable

        test_file = self.config["test_dir"] + DIR_SEPARATOR + test_filename
        return os.path.exists(test_file)


    # @brief Checks if a given directory is a stest environment
    # @param path Path to the directory
    # @return True if the directory is a stest environment, False otherwise
    def __dir_is_stest_environment(self, path: str) -> bool:
        return os.path.exists(path + DIR_SEPARATOR + STEST_DIR + DIR_SEPARATOR + STEST_CONFIG_FILE)


    # @brief Creates the default config file
    # @param path Path to the config file
    def __create_config_file(self, path: str, test_dir: str, language: str) -> None:
        DEFAULT_CONFIG["language"] = language
        DEFAULT_CONFIG["test_framework"] = TESTING_FRAMEWORKS[language]
        DEFAULT_CONFIG["test_dir"] = utils.relative_path_to_absolute_path(test_dir)
        with open(path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)


    # @brief Loads the config file
    # @param path Path to the config file
    def __load_config_file(self, path: str) -> None:
        with open(path, "r") as f:
            self.config = json.load(f)


    # @brief Saves the config file
    # @param path Path to the config file
    def __save_config_file(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.config, f, indent=4)


    # @brief Fetches the root of the stest environment
    #
    # @details This method will search for the stest environment
    #          by looking for the config file in the current directory
    #          and its parent directories (up to MAX_PARENT_SEARCH_DEPTH).
    #
    #          This makes it possible to run stest from a subdirectory
    #          of the stest environment, just like in git.
    #
    #          Returns the path to the stest environment root (.stest directory)
    #          or None if the stest environment could not be found.
    #
    # @return Path to the stest environment root or None if the stest environment could not be found
    def __fetch_stest_environment_root(self) -> str:
        cwd = os.getcwd()
        for _ in range(MAX_PARENT_SEARCH_DEPTH):
            if self.__dir_is_stest_environment(cwd):
                return cwd + DIR_SEPARATOR + STEST_DIR

            cwd = os.path.dirname(cwd)

        return None


    # @brief Checks if a file is being tracked by stest
    # @param file Path to the file
    def __file_is_tracked(self, file: str) -> bool:
        return file in self.config["tracked_files"]


    # @brief Checks if a file has changed
    # @param file Path to the file
    # @return True if the file has changed, False otherwise
    def __file_has_changed(self, file: str) -> bool:
        if not self.__file_is_tracked(file):
            return False

        file_hash = utils.get_file_hash(file)
        return file_hash != self.config["tracked_files"][file]["hash"]


    # @brief Checks if the content of a file matches the given language
    # @param file Path to the file
    # @param language Language to check
    # @return True if the content of the file matches the language, False otherwise
    def __file_content_matches_language(self, file: str, language: str) -> bool:
        initial_prompt = prompts.CHECK_FILE_LANGUAGE_PROMPT.replace("{language}", language)
        file_content = utils.get_file_content(file)
        response = self.openai_iface.send_data_in_chunks_and_get_response(initial_prompt, file_content)
        return response[:3] == "Yes"


    # @brief Sets a file as tracked
    #
    # @details Checks if the file is already being tracked
    #          and if not, adds it to the tracked files along
    #          with the file hash to check for changes
    #
    # @param file Path to the file
    def __track_file(self, file: str) -> None:
        if not self.__file_is_tracked(file):
            if not self.__file_content_matches_language(file, self.config["language"]):
                raise Exception(f"File {file} does not match the current language defined for the test environment: {self.config['language']} so it's being ignored")

            absolute_path = utils.relative_path_to_absolute_path(file)

            self.config["tracked_files"][absolute_path] = {
                "hash": ""
            }

            self.__save_config_file(self.stest_environment_root + DIR_SEPARATOR + STEST_CONFIG_FILE)

     
    # @brief Tracks all files in a given directory
    # @param directory Path to the directory
    def __track_all_files_in_directory(self, directory: str) -> None:
        for root, dirs, files in os.walk(directory):
            for file in files:
                try:
                    self.__track_file(file)
                except Exception as e:
                    print(e)

    
    # @brief Untracks a file
    # @param file Path to the file
    def __untrack_file(self, file: str) -> None:
        absolute_path = utils.relative_path_to_absolute_path(file)

        if absolute_path in self.config["tracked_files"]:
            del self.config["tracked_files"][absolute_path]
        else:
            raise Exception(f"The file {file} is not being tracked.")

        self.__save_config_file(self.stest_environment_root + DIR_SEPARATOR + STEST_CONFIG_FILE)


    # @brief Untracks all files in a given directory
    # @param directory Path to the directory
    def __untrack__all_files_in_directory(self, directory: str) -> None:
        for root, dirs, files in os.walk(directory):
            for file in files:
                try:
                    self.__untrack_file(file)
                except Exception as e:
                    print(e)


    # @brief Builds the serialized data for a file
    #
    # @details The serialized data for a file is the file content
    #          formatted in a way that Chat GPT can understand and parse.
    #          (check prompts.py/CREATE_TESTS_PROMPT for details)
    #
    # @param path Path to the file
    # @return Serialized data for the file
    def __build_serialized_file_data(self, path: str) -> str:
        file_content = utils.get_file_content(path)
        return FILE_START_DELIMITER + "\n" + utils.get_filename(path) + file_content + "\n"


    # @brief Builds the serialized data for a file that was previously tested
    #
    # @details The serialized data for a file that was previously tested
    #          is the file content formatted in a way that Chat GPT can understand
    #          and parse. (check prompts.py/CREATE_TESTS_REFACTOR_PROMPT for details)
    #
    # @param path Path to the file
    # @return Serialized data for the file
    def __build_serialized_previous_test_file_data(self, path: str) -> str:
        file_content = utils.get_file_content(path)
        return PREV_TEST_FILE_START_DELIMITER + "\n" + utils.get_filename(path) + file_content + "\n"


    # @brief Saves the returned tests from Chat GPT into a file 
    #
    # @details The returned tests from Chat GPT are a list of strings
    #          that represent the tests that were generated for a given file.
    #          
    #          The output is formatted in the same way as the serialized data
    #          that was sent to Chat GPT. (check prompts.py/CREATE_TESTS_PROMPT for details)
    #
    # @param path Path to the file
    # @param data Data to save
    def __save_serialized_test_data(self, path: str, data: str) -> None:
        files = []

        # I've had to change this to a more complex regex because
        # the previous one was not working properly sometimes
        #
        # This is what I had before: re.compile(r'```.*?```', re.DOTALL) 
        # If anyone in the jury knows why this is happening, please let me know.
        # But let's be honest, no one knows regex; and if they say they do, they're lying.
        pattern = r'```[a-zA-Z]*\n([\s\S]*?)\n```'

        for file_data in data.split(FILE_START_DELIMITER):
            if file_data == "":
                continue
            
            lines = file_data.split("\n")
            file_name = lines[1]
            file_content = "\n".join(lines[2:])

            filtered_file_content = re.sub(pattern, r'\1', file_content)

            files.append({
                "name": file_name,
                "content": filtered_file_content
            })

        for file in files:
            file_path = path + DIR_SEPARATOR + file["name"]
            with open(file_path, "w") as f:
                f.write(file["content"])
 

