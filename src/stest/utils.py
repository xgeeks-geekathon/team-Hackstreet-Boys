import os
import hashlib

# @brief Create a directory if it does not exist
# @param path Path to the directory
def create_dir(str: path) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


# @brief Returns the SHA-256 hash of the given file
# @param file Path to the file
# @return hash_digest
def get_file_hash(str: file) -> str:
    with open(file, "rb") as f:
        bytes = f.read()
        digest = hashlib.sha256(bytes).hexdigest()
        return digest


def get_file_content(str: file) ->  

