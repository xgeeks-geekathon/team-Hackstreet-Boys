import unittest
from car import Car

class CarTest(unittest.TestCase):
    def setUp(self):
        self.car = Car("ABC1234", "red", 2000)

    def test_initial_car_properties(self):
        self.assertEqual(self.car.get_plate(), "ABC1234")
        self.assertEqual(self.car.get_color(), "red")
        self.assertEqual(self.car.get_cc(), 2000)
        self.assertEqual(self.car.get_passengers(), [])

    def test_set_plate(self):
        self.car.set_plate("XYZ789")
        self.assertEqual(self.car.get_plate(), "XYZ789")

    def test_set_color(self):
        self.car.set_color("blue")
        self.assertEqual(self.car.get_color(), "blue")

    def test_set_cc(self):
        self.car.set_cc(1500)
        self.assertEqual(self.car.get_cc(), 1500)

    def test_add_passenger(self):
        self.car.add_passenger("John Doe")
        self.assertEqual(self.car.get_passengers(), ["John Doe"])

    def test_remove_passenger(self):
        self.car.add_passenger("John Doe")
        self.assertEqual(self.car.get_passengers(), ["John Doe"])
        self.car.remove_passenger("John Doe")
        self.assertEqual(self.car.get_passengers(), [])


if __name__ == "__main__":
    unittest.main()
