import unittest

from ..parameter_interpreter import ParameterInterpreter, Parameter, ParameterException








class TestParameterInterpreter(unittest.TestCase):

    def test_init(self):
        interpreter = ParameterInterpreter()
        self.assertFalse(interpreter._combine_until_closing_bracked)

    def test_add_parameter(self):
        param1 = Parameter("param1")
        param2 = Parameter("param2")
        interpreter = ParameterInterpreter()
        interpreter.addParameter(param1)
        interpreter.addParameter(param2)
        parameter_list = interpreter.getParameterList()
        self.assertIn(param1, parameter_list)
        self.assertIn(param2, parameter_list)

    def test_interpret_list(self):
        param1 = Parameter("param1", args=["-p1"])
        param2 = Parameter("param2", args=["-p2"], needsValue=True)
        interpreter = ParameterInterpreter()
        interpreter.addParameter(param1)
        interpreter.addParameter(param2)

        arg_list = ["program_name", "-p1", "value1", "-p2", "value2"]
        interpreter.interpretList(arg_list)
        
        self.assertEqual(param1.getFlag(), True)
        self.assertEqual(param2.getFlag(), True)
        self.assertEqual(param1.getValue(), None)
        self.assertEqual(param2.getValue(), "value2")

    def test_interpret_list_missing_value(self):
        param = Parameter("param", args=["-p"], needsValue=True)
        interpreter = ParameterInterpreter()
        interpreter.addParameter(param)

        arg_list = ["program_name", "-p"]
        with self.assertRaises(ParameterException):
            interpreter.interpretList(arg_list)

    def test_interpret_list_flag_param(self):
        param = Parameter("param", args=["-p"])
        interpreter = ParameterInterpreter()
        interpreter.addParameter(param)

        arg_list = ["program_name", "-p"]
        interpreter.interpretList(arg_list)
        self.assertEqual(param.getFlag(), True)


if __name__ == '__main__':
    unittest.main()



