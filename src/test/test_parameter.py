import unittest

from ..parameter_interpreter import Parameter, ParameterException


class TestParameter(unittest.TestCase):

    def test_init(self):
        # Testen der Initialisierung der Parameterklasse
        param = Parameter("param_name")
        self.assertEqual(param.getName(), "param_name")
        self.assertEqual(param.needsValue, True)
        self.assertEqual(param.args, [])
        self.assertEqual(param.getValue(), None)
        self.assertEqual(param.getFlag(), False)
        self.assertEqual(param.helpText, "")
        self.assertEqual(param.multi_arguments, False)

    def test_set_value(self):
        # Testen des Setzens von Werten für den Parameter
        param = Parameter("param_name")
        param.setValue(42)
        self.assertEqual(param.getValue(), 42)
        param.setValue("string_value")
        self.assertEqual(param.getValue(), "string_value")

    def test_set_flag(self):
        # Testen des Setzens der Flagge für den Parameter
        param = Parameter("param_name")
        self.assertEqual(param.getFlag(), False)
        param.setFlag()
        self.assertEqual(param.getFlag(), True)

    def test_value_type_casting(self):
        # Testen des Typen-Castings für Parameter
        param_int = Parameter("param_int", expectType=int)
        param_int.setValue("42")
        self.assertEqual(param_int.getValue(), 42)

        param_float = Parameter("param_float", expectType=float)
        param_float.setValue("3.14")
        self.assertEqual(param_float.getValue(), 3.14)
        param_float.setValue("3.14e-2")                     # test scientific notation value
        self.assertEqual(param_float.getValue(), 0.0314)

    def test_value_type_casting_failure(self):
        # Testen des Fehlschlagens des Typen-Castings für Parameter
        param_int = Parameter("param_int", expectType=int)
        with self.assertRaises(ParameterException):
            param_int.setValue("not_an_integer")

    def test_multi_arguments(self):
        # Testen von multi_arguments-Einstellungen
        param_multi = Parameter("param_multi", multi_arguments=True)
        param_multi.setValue(1)
        self.assertEqual(param_multi.getValue(), 1)
        param_multi.setValue([1, 2, 3])
        self.assertEqual(param_multi.getValue(), [1, 2, 3])
        




