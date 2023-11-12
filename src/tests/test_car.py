import unittest
from car import Car

class TestCar(unittest.TestCase):

    def setUp(self):
        self.car = Car('123ABC', 'Black', 1000)

    def test_get_plate(self):
        self.assertEqual(self.car.get_plate(), '123ABC')

    def test_set_plate(self):
        self.car.set_plate('456DEF')
        self.assertEqual(self.car.get_plate(), '456DEF')

    def test_get_color(self):
        self.assertEqual(self.car.get_color(), 'Black')

    def test_set_color(self):
        self.car.set_color('Red')
        self.assertEqual(self.car.get_color(), 'Red')

    def test_get_cc(self):
        self.assertEqual(self.car.get_cc(), 1000)

    def test_set_cc(self):
        self.car.set_cc(1500)
        self.assertEqual(self.car.get_cc(), 1500)

    def test_passengers(self):
        self.assertListEqual(self.car.get_passengers(), [])
        self.car.add_passenger('John')
        self.assertListEqual(self.car.get_passengers(), ['John'])
        self.car.remove_passenger('John')
        self.assertListEqual(self.car.get_passengers(), [])
        with self.assertRaises(Exception) as context:
            self.car.remove_passenger('John')
        self.assertTrue('Passenger John not found in the car.' in str(context.exception))

if __name__ == '__main__':
    unittest.main()
