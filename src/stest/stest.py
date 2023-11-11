import json
import os

# Local imports
from . import utils
from .openai_iface import IOpenAI
from . import prompts

########################################################################

# List of supported languages
SUPPORTED_LANGUAGES = ["c", "cpp", "py", "js"]

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
    "output_dir": "",
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
    def __create_config_file(self, inPath: str, outPath: str,language: str) -> None:
        DEFAULT_CONFIG["language"] = language
        DEFAULT_CONFIG["test_framework"] = TESTING_FRAMEWORKS[language]
        DEFAULT_CONFIG["output_dir"] = outPath
        with open(inPath, "w") as f:
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
    async def __file_content_matches_language(self, file: str, language: str) -> bool:
        initial_prompt = prompts.CHECK_FILE_LANGUAGE_PROMPT.replace("{language}", language)
        file_content = utils.get_file_content(file)  # Assuming this is a synchronous function
        response = await self.openai_iface.send_data_in_chunks_and_get_response(initial_prompt, file_content)
        file_extension = file.split(".")[-1]
        return "Yes" in response and file_extension in SUPPORTED_LANGUAGES

    # @brief Sets a file as tracked
    #
    # @details Checks if the file is already being tracked
    #          and if not, adds it to the tracked files along
    #          with the file hash to check for changes
    #
    # @param file Path to the file
    async def __track_file(self, file: str) -> None:
        if not self.__file_is_tracked(file):
            if not await self.__file_content_matches_language(file, self.config["language"]):
                raise Exception(f"File {file} does not match the current language defined for the test environment: {self.config['language']} so it's being ignored")

            self.config["tracked_files"][file] = {
                "hash": utils.get_file_hash(file),
            }
            self.__save_config_file(STEST_DIR + DIR_SEPARATOR + STEST_CONFIG_FILE)

    # @brief Tracks all files in a given directory
    async def __track_all_files_in_directory(self, directory: str) -> None:
        for root, dirs, files in os.walk(directory):
            for file in files:
                try:
                    file = os.path.join(root, file)
                    await self.__track_file(file)
                except Exception as e:
                    print(e)

    ###############################
    # Public methods              #
    ###############################

    # @brief Initializes a new stest environment
    # @param path Path to the stest environment
    def init(self, inPath: str, outPath: str,language: str) -> None:
        if self.__cwd_is_stest_environment():
            raise Exception("The current directory already contains a stest environment.")

        utils.create_dir(inPath + DIR_SEPARATOR + STEST_DIR)
        config_file_path = inPath + DIR_SEPARATOR + STEST_DIR + DIR_SEPARATOR + STEST_CONFIG_FILE
        self.__create_config_file(config_file_path, outPath, language)
        self.__load_config_file(config_file_path)
        print("Initialized empty stest environment.")

    # @brief Adds a list of files to the tracked files
    # @param paths List of paths to the files 
    async def add(self, paths: list[str]) -> None:
        if not self.__cwd_is_stest_environment():
            raise Exception("The current directory is not a stest environment.")

        self.__load_config_file(STEST_DIR + DIR_SEPARATOR + STEST_CONFIG_FILE)

        for path in paths:
            if not os.path.exists(path):
                raise Exception(f"No such file or directory: {path}")
            elif utils.is_dir(path):
                await self.__track_all_files_in_directory(path)
            elif self.__file_is_tracked(path):
                raise Exception(
                    f"The file {path} is already being tracked. Use 'stest remove' to stop tracking the file.")
            else:
                await self.__track_file(path)

    # @brief Removes a list of files from the tracked files
    # @param paths List of paths to the files
    def remove(self, paths: list[str]) -> None:
        if not self.__cwd_is_stest_environment():
            raise Exception("The current directory is not a stest environment.")

        self.__load_config_file(STEST_DIR + DIR_SEPARATOR + STEST_CONFIG_FILE)

        for path in paths:

            if not os.path.exists(path):
                raise Exception(f"No such file or directory: {path}")
            elif os.path.exists(path):
                self.__untrack_files_in_directory(path)
            elif not self.__file_is_tracked(path) and not utils.is_dir(path):
                raise Exception(f"The file {path} is not being tracked.")
            else:
                self.__untrack_file(path)

        self.__save_config_file(STEST_DIR + DIR_SEPARATOR + STEST_CONFIG_FILE)

    # @brief Removes a file from the tracked files
    # @param file Path to the file
    def __untrack_file(self, file: str) -> None:
        if file in self.config["tracked_files"]:
            del self.config["tracked_files"][file]
        else:
            raise Exception(f"The file {file} is not being tracked.")

    # @brief Removes all files in a given directory from the tracked files
    # @param directory Path to the directory
    def __untrack_files_in_directory(self, directory: str) -> None:
        for root, dirs, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                if self.__file_is_tracked(full_path):
                    self.__untrack_file(full_path)

    # @brief Creates the tests for the tracked files
    def create_tests(self) -> None:
        if not self.__cwd_is_stest_environment():
            raise Exception("The current directory is not a stest environment.")

        for file in self.config["tracked_files"]:
            if self.__file_has_changed(file):
                print("File has changed: {}".format(file))
