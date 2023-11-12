# Stest

Stest (**Smart Test**) is a compreensive command line tool that automatically generates unit tests for your code using artificial intelligence.

## Demo

![Demo]()

## Installation

```bash
# Clone the repo
git clone git@github.com:xgeeks-geekathon/team-Hackstreet-Boys.git
cd team-Hackstreet-Boys

sudo ./build.sh  # Linux and MacOS
# or
./build.bat # Windows (admin privileges required)
```

The compiled binaries will be located in the `dist` directory.

## Documentation

**Stest is not a simple command line tool.** It is a complete testing environment that allows you to create and manage your tests using a simple command line interface.

If you want to learn more about stest, check out the [documentation](https://stest.readthedocs.io/en/latest/).

## Usage

#### Init a new __stest__ testing environment.

```bash
stest init [path] -o [tests_dir] --language [language] # Inits a new stest testing environment
```

##### Supported languages:
- Python (`py`)
- JavaScript (`js`)
- C (`c`)
- C++ (`cpp`)

#### Add files to the testing environment.

```bash
stest add [file1] [file2] # Adds files to the testing environment
stest add . # Adds all files in the current directory to the testing environment
```

#### Create tests for the currently tracked files.
```bash
stest create-tests # Creates tests for the currently tracked files
```

## Example

#### Create a new Python project

```bash
mkdir my_project
cd my_project
touch main.py
touch car.py
```

#### Add some code to the files

```python
# main.py
from car import Car

def main():
   car = Car()
   car.drive()

if __name__ == '__main__':
   main()
```


```python
# car.py
class Car:
   def __init__(self):
      self.speed = 0

   def drive(self):
      self.speed = 100
```

#### Init a new stest testing environment

```bash
stest init . -o tests --language python
```

#### Add the files to the testing environment

```bash
stest add car.py
```

#### Create tests for the currently tracked files

```bash
stest create-tests
```

The tests will be written to the `tests`  directory specified using the `-o` flag when initializing the testing environment.

```python
# tests/test_car.py
import unittest
from car import Car

class TestCar(unittest.TestCase):
   def test_drive(self):
      car = Car()
      car.drive()
      self.assertEqual(car.speed, 100)

if __name__ == '__main__':
      unittest.main()
```

## What's next?

#### Add support for more languages and testing frameworks

The 

- [ ] Add support for more languages
- [ ] Add support for more testing frameworks
- [ ] Add test execution and output analysis
