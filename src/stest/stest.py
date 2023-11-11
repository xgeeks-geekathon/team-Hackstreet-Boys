import json

# Local imports
import utils


SUPPORTED_LANGUAGES = [
    "c",
    "cpp",
    "py",
    "js"
]


DEFAULT_CONFIG = {
    "tracked_files": {},
    "language": "",
    "test_framework": "",
    "test_command": "",
}


class Stest:
    def __init__(self):
        self.config = None


    ###############################
    # Public methods              #
    ###############################

    # @brief Initializes a new stest environment
    # @param path Path to the stest environment
    def init(self, str: path) -> None:
        utils.create_dir(path)
        self.__create_config_file(path)
        self.__load_config_file(path)
        print("Initialized empty stest environment.")


    # @brief Adds a file to the tracked files
    # @param file Path to the file
    def add(self, str: file) -> None:
        pass


    # @brief Creates the tests for the tracked files
    def create_tests(self) -> None:
        for file in self.config["tracked_files"]:
            if self.__file_has_changed(file):
                print("File has changed: {}".format(file))


    ###############################
    # Private methods             #
    ###############################

    # @brief Creates the default config file
    # @param path Path to the config file
    def __create_config_file(self, str: path) -> None:
        with open(path + "/config.json", "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)


    # @brief Loads the config file
    # @param path Path to the config file
    def __load_config_file(self, str: path) -> None:
        with open(path, "r") as f:
            self.config = json.load(f)


    # @brief Saves the config file
    # @param path Path to the config file
    def __save_config_file(self, str: path) -> None:
        with open(path, "w") as f:
            json.dump(self.config, f, indent=4)


    # @brief Checks if a file is being tracked by stest
    # @param file Path to the file
    def __file_is_tracked(self, str: file) -> bool:
        return file in self.config["tracked_files"]


    # @brief Checks if a file has changed
    # @param file Path to the file
    # @return True if the file has changed, False otherwise
    def __file_has_changed(self, str: file) -> bool:
        if not self.__file_is_tracked(file):
            return False

        file_hash = utils.get_file_hash(file)
        if file_hash != self.config["tracked_files"][file]["hash"]:
            return True

        return False


    # @brief Checks if a given directory is a stest environment
    # @return True if the directory is a stest environment, False otherwise
    def __cwd_is_stest_environment(self) -> bool:
        if not os.path.exists(".stest"):
            return False

        if not os.path.isfile(".stest/config.json"):
            return False

        return True

    
    # @brief Checks if a given language is supported
    # @param language Language to check
    # @return True if the language is supported, False otherwise
    def __language_is_supported(self, str: language) -> bool:
        return language in SUPPORTED_LANGUAGES

