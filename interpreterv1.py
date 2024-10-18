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

    def var_helper(self, varName):
        if varName not in self.vars:
            self.error_helper(f"Variable {varName} was not defined")
        return self.vars[varName]
    
    def function_helper(self, expression):
        args = expression.get("args")
        for i in range(len(args)):
            args[i] = self.evaluate_expression(args[i])
        name = expression.get("name")
        if name == "print":                 # todo: make a custom print function; call super output function
            print(*args)
            return
        elif name != "inputi":
            self.error_helper(f"Function {name} has not been defined")
        globals()[expression.get("name")](*args)

    def evaluate_expression(self, expression):  # expression can be an Expression, Variable, or Value node
        t = expression.elem_type
        if t == "var":
            return self.var_helper(expression.get("name"))
        if t == "int" or t == "string":
            return expression.get("val")
        # expression node
        if t=="+":
            return self.evaluate_expression(expression.get("op1")) + self.evaluate_expression(expression.get("op2"))
        if t=="-":
            return self.evaluate_expression(expression.get("op1")) - self.evaluate_expression(expression.get("op2"))
        if t=="fcall":
            self.function_helper(expression)
    
    def run(self, program):
        parsed_program = parse_program(program)
        # print(parsed_program)
        # print("--------")
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
}
"""
)