import os
import hashlib


# @brief Create a directory if it does not exist
# @param path Path to the directory
def create_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


# @brief Returns the SHA-256 hash of the given file
# @param file Path to the file
# @return hash_digest
def get_file_hash(file: str) -> str:
    with open(file, "rb") as f:
        bytes = f.read()
        digest = hashlib.sha256(bytes).hexdigest()
        return digest


# @brief Returns the content of the given file
# @param file Path to the file
# @return content
def get_file_content(file: str) -> str:
    with open(file, "r") as f:
        return f.read()


# @brief Checks if the current OS is POSIX
# @return True if the OS is POSIX, False otherwise
def is_posix():
    return os.name == "posix"


# @brief Checks if the given path is a directory
# @param path Path to the directory
# @return True if the path is a directory, False otherwise
def is_dir(path: str) -> bool:
    return os.path.isdir(path)


# @brief Converts the given relative path into an absolute path
# @param path Relative path
# @return absolute_path
def relative_path_to_absolute_path(path: str) -> str:
    return os.path.abspath(path)


# @brief Returns the filename from the given path
# @param path Path to the file
# @return filename
def get_filename(path: str) -> str:
    return os.path.basename(path)

