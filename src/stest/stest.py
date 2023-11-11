import json
import os

# Local imports
from . import utils
from .openai_iface import IOpenAI

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


########################################################################

class Stest:
    def __init__(self):
        self.config = None
        self.openai_iface = IOpenAI()

    ###############################
    # Private methods             #
    ###############################

    # @brief Checks if a given directory is a stest environment
    # @return True if the directory is a stest environment, False otherwise
    def __cwd_is_stest_environment(self) -> bool:
        if not os.path.exists(STEST_DIR):
            return False

        if not os.path.isfile(STEST_DIR + DIR_SEPARATOR + STEST_CONFIG_FILE):
            return False

        return True

    # @brief Creates the default config file
    # @param path Path to the config file
    def __create_config_file(self, path: str, language: str) -> None:
        DEFAULT_CONFIG["language"] = language
        DEFAULT_CONFIG["test_framework"] = TESTING_FRAMEWORKS[language]
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
        if file_hash != self.config["tracked_files"][file]["hash"]:
            return True

        return False

    # @brief Checks if the content of a file matches the given language
    # @param file Path to the file
    # @param language Language to check
    # @return True if the content of the file matches the language, False otherwise
    def __file_content_matches_language(self, file: str, language: str) -> bool:
        initial_prompt = f"Is the following file written in {language}?"
        file_content = utils.get_file_content(file)
        response = self.openai_iface.send_data_in_chunks_and_get_response(initial_prompt, file_content)
        return response["choices"][0]["text"] == "Yes"

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
                raise Exception(
                    f"File {file} does not match the current language: {self.config['language']} so it's being ignored")

            self.config["tracked_files"][file] = {
                "hash": utils.get_file_hash(file),
            }
            self.__save_config_file(STEST_DIR + DIR_SEPARATOR + STEST_CONFIG_FILE)

    # @brief Tracks all files in a given directory
    def __track_all_files_in_directory(self, directory: str) -> None:
        for root, dirs, files in os.walk(directory):
            for file in files:
                try:
                    self.__track_file(file)
                except Exception as e:
                    print(e)

    ###############################
    # Public methods              #
    ###############################

    # @brief Initializes a new stest environment
    # @param path Path to the stest environment
    def init(self, path: str, language: str) -> None:
        if self.__cwd_is_stest_environment():
            raise Exception("The current directory already contains a stest environment.")

        utils.create_dir(path + DIR_SEPARATOR + STEST_DIR)
        config_file_path = path + DIR_SEPARATOR + STEST_DIR + DIR_SEPARATOR + STEST_CONFIG_FILE
        self.__create_config_file(config_file_path, language)
        self.__load_config_file(config_file_path)
        print("Initialized empty stest environment.")

    # @brief Adds a list of files to the tracked files
    # @param paths List of paths to the files 
    def add(self, paths: list[str]) -> None:
        if not self.__cwd_is_stest_environment():
            raise Exception("The current directory is not a stest environment.")

        self.__load_config_file(STEST_DIR + DIR_SEPARATOR + STEST_CONFIG_FILE)

        for path in paths:
            if not os.path.exists(path):
                raise Exception(f"No such file or directory: {path}")
            elif utils.is_dir(path):
                pass

            elif self.__file_is_tracked(path):
                raise Exception(
                    f"The file {path} is already being tracked. Use 'stest remove' to stop tracking the file.")
            else:
                self.__track_file(path)

    # @brief Creates the tests for the tracked files
    def create_tests(self) -> None:
        if not self.__cwd_is_stest_environment():
            raise Exception("The current directory is not a stest environment.")

        for file in self.config["tracked_files"]:
            if self.__file_has_changed(file):
                print("File has changed: {}".format(file))
