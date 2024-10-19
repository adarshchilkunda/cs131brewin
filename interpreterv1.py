from intbase import ErrorType, InterpreterBase
from brewparse import parse_program

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.vars = {}


    def error_helper(self, message):
        super().error(
            ErrorType.NAME_ERROR,
            message
        )
    def type_error_helper(self, message):
        super().error(
            ErrorType.TYPE_ERROR,
            message
        )

    def var_helper(self, varName):
        if varName not in self.vars:
            self.error_helper(f"Variable {varName} was not defined")
        return self.vars[varName]

    def custom_print(self, *messages):
        finalString = ""
        for message in messages:
            finalString += str(message)
        super().output(finalString)
    
    def inputi(self, prompt=None):
        if prompt is not None:
            super().output(prompt)
        inp = super().get_input()
        intInp = int(inp)
        return intInp

    def function_helper(self, expression):
        args = expression.get("args")
        for i in range(len(args)):
            args[i] = self.evaluate_expression(args[i])
        name = expression.get("name")
        if name == "print":                 # todo: make a custom print function; call super output function
            self.custom_print(*args)
            return
        elif name == "inputi":
            print("args:" + str(args))
            if len(args) > 1:
                self.error_helper(f"No inputi() function found that takes > 1 parameter")
            if len(args) == 1:
                return self.inputi((args[0]))
            return self.inputi()
        else:
            self.error_helper(f"Function {name} has not been defined")
        # globals()[name](*args)

    def evaluate_expression(self, expression):  # expression can be an Expression, Variable, or Value node
        t = expression.elem_type
        if t == "var":
            return self.var_helper(expression.get("name"))
        if t == "int" or t == "string":
            return expression.get("val")
        # expression node
        if t=="+":
            op1 = self.evaluate_expression(expression.get("op1"))
            op2 = self.evaluate_expression(expression.get("op2"))
            if not isinstance(op1, int) or not isinstance(op2, int):
                print(type(op1))
                print(type(op2))
                self.type_error_helper("Incompatible types for arithmetic operation")
            return op1 + op2
        if t=="-":
            op1 = self.evaluate_expression(expression.get("op1"))
            op2 = self.evaluate_expression(expression.get("op2"))
            if not isinstance(op1, int) or not isinstance(op2, int):
                self.type_error_helper("Incompatible types for arithmetic operation")
            return op1 - op2
        if t=="fcall":
            return self.function_helper(expression)
    
    def run(self, program):
        parsed_program = parse_program(program)
        for element in parsed_program.get("functions"):
            name = element.get("name")
            # only one function for now; return an error if that function is not main
            if name != "main":
                self.error_helper("No main() function was found")

            statements = element.get("statements")
            for statement in statements:
                stateType = statement.elem_type
                if stateType == "vardef":               # define variable but no value
                    varName = statement.get("name")
                    if varName not in self.vars:
                        self.vars[varName] = None
                    else:
                        self.error_helper(f"Variable {varName} defined more than once")
                elif stateType == "=":                  # assign expression to variable
                    varName = statement.get("name")
                    rhsNode = statement.get("expression")
                    if varName not in self.vars:
                        super().error()
                    self.vars[varName] = self.evaluate_expression(rhsNode)
                elif stateType == "fcall":
                    self.function_helper(statement)
        

if __name__ == "__main__":
    interpreter = Interpreter()
    interpreter.run("""func main() {
    var x;
    x = 5 + 6;
    print("The sum is: ", x);
    print(3 + 5);
    print(4 + inputi("enter a number: "));
    print(3 - (3 + (2 + inputi())));
}
"""
)