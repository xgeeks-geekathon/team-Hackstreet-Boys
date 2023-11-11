# Stest

AI powered universal unit testing tool.

## Usage

#### Init a new __stest__ testing environment.

```bash
stest init [path] -o [tests_dir] --language [language] # Inits a new stest testing environment
```

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