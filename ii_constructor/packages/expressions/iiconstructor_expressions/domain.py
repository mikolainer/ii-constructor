from iiconstructor_expressions.primitives import ExprType, EqType

class Iexpression:
    pass

class Expression(Iexpression):
    def __init__(self, field_name:str, field_value, expr_type: ExprType):
        setattr(self, "_Expression__field_name", field_name)
        setattr(self, "_Expression__field_value", field_value)
        setattr(self, "_Expression__field_type", expr_type)

    def name(self) -> str:
        return getattr(self, "_Expression__field_name")

    def value(self):
        return getattr(self, "_Expression__field_value")
    
    def type(self) -> ExprType:
        return getattr(self, "_Expression__field_type")
    
class EqExpression(Expression):
    def __init__(self, field_name, field_value):
        super().__init__(field_name, field_value, EqType())
