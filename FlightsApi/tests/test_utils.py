from unittest import TestCase as BasicTestCase
from ..utils.typechecking import accepts
from ..utils.exceptions import IncorrectTypePassedToFunctionException

class TestAccepts(BasicTestCase):
    @staticmethod
    @accepts(int, str, bool)
    def dummy_func(integer, string, boolean):
        if  (type(integer) is not int) or \
            (type(string) is not str) or \
            (type(boolean) is not bool):
            return "Failure"
        else:
            return "Success"
                    
    def test_accepts_empty_variables(self):
        @accepts()
        def local_dummy():
            return "Success"
        self.assertEqual("Success", local_dummy())
                    
    def test_accepts_correct_types(self):
        self.assertEqual("Success", self.dummy_func(1, "1", True))
    
    def test_accepts_blocked_variables(self):
        with self.subTest("Bad int"):
            self.assertRaises(IncorrectTypePassedToFunctionException, lambda: self.dummy_func("err", "1", True))
        with self.subTest("Bad string"):
            self.assertRaises(IncorrectTypePassedToFunctionException, lambda: self.dummy_func(1, 1, True))
        with self.subTest("Bad bool"):
            self.assertRaises(IncorrectTypePassedToFunctionException, lambda: self.dummy_func(1, "1", "err"))
            
    def test_accepts_kwarg_mix(self):
        with self.subTest("Half kwargs"):
            self.assertEqual("Success", self.dummy_func(1, "1", boolean=True))
            self.assertRaises(IncorrectTypePassedToFunctionException, lambda: self.dummy_func("err", "1", boolean=True))
            self.assertRaises(IncorrectTypePassedToFunctionException, lambda: self.dummy_func(1, "1", boolean="err"))
        
        with self.subTest("Only kwargs"):
            self.assertEqual("Success", self.dummy_func(integer=1, string="1", boolean=True))
            self.assertEqual("Success", self.dummy_func(integer=1, boolean=True, string="1")) # Shuffled
            self.assertRaises(IncorrectTypePassedToFunctionException, lambda: self.dummy_func(integer="err", string="1", boolean=True))
            self.assertRaises(IncorrectTypePassedToFunctionException, lambda: self.dummy_func(integer=1, string="1", boolean="err"))
            self.assertRaises(IncorrectTypePassedToFunctionException, lambda: self.dummy_func(string="1", integer=1, boolean="err")) # Shuffled