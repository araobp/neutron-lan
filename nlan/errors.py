class NlanException(Exception):

    def __init__(self, message, result=None):

        self.message = message
        self.result = result

    def __str__(self):
        return self.message
    
    def get_result(self):
        return self.result 

class ModelError(Exception):

    def __init__(self, message, model=None, params=None):

        self.message = message
        self.model = model
        self.params = params

    def __str__(self):

        if self.model and self.params:
            message = "{}\nmodel: {}\nparams: {}".format(self.message, str(self.model), str(self.params))
        elif self.model:
            message = "{}\nmodel: {}".format(self.message, str(self.model))
        elif self.params:
            message = "{}\nparams: {}".format(self.message, str(self.params))
        else:
            message = "{}".format(self.message)

        return message


class SubprocessError(Exception):

    def __init__(self, message, command=None):

        self.message = message
        self.command = command 

    def __str__(self):

        message = '' 
        if self.command:
            message = "{}\ncommand:{}".format(self.message, self.command)
        else:
            message = self.message

        return message

if __name__ == '__main__':
    
    import unittest
    
    class TestSequenceFunctions(unittest.TestCase):

        def testNlanException(self):
            message = 'TEST'
            result = 'XXX' 
            with self.assertRaises(NlanException):
                try:
                    raise NlanException(message=message, result=result)
                except NlanException as e:
                    self.assertEqual(str(e), message)
                    self.assertEqual(str(e.get_result()), str(result))
                    raise

        def testModelError(self):

            model = {'a': 1, 'b': 'c'}
            params = ['a', 'b']
            message = 'TEST'
            result = "{}\nmodel: {}\nparams: {}".format(message, str(model), str(params))
            with self.assertRaises(ModelError):
                try:
                    raise ModelError(message=message, model=model, params=params)
                except ModelError as e:
                    self.assertEqual(str(e), result)
                    raise

        def testSubprocessError(self):
            
            message = 'TEST'
            command = 'cmd a b c'
            result = "{}\ncommand:{}".format(message, command)
            with self.assertRaises(SubprocessError):
                try:
                    raise SubprocessError(message=message, command=command)
                except SubprocessError as e:
                    self.assertEqual(str(e), result)
                    raise

    unittest.main(verbosity=2)

