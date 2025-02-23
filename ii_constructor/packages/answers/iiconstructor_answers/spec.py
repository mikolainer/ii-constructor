class Iexpression:
    pass

class Expression(Iexpression):
    def __init__(self, field_name:str, field_value):
        setattr(self, "_Expression__field_name", field_name)
        setattr(self, "_Expression__field_value", field_value)

    def name(self) -> str:
        return getattr(self, "_Expression__field_name")

    def value(self):
        return getattr(self, "_Expression__field_value")

#class ComplexExpression(Iexpression):
#    __left: Iexpression
#    __right: Iexpression
#
#    def __init__(self, left:Iexpression, right:Iexpression):
#        setattr(self, "_ComplexExpression__left", left)
#        setattr(self, "_ComplexExpression__right", right)
#        
#    def left(self) -> Iexpression:
#        return getattr(self, "_ComplexExpression__left")
#    
#    def right(self) -> Iexpression:
#        return getattr(self, "_ComplexExpression__right")
    