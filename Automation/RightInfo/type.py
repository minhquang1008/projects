from abc import ABC, abstractmethod


class Ratio(ABC):

    @abstractmethod
    def __init__(self, inputValue):
        pass
    
    @property
    @abstractmethod
    def value(self):
        pass
    
    @abstractmethod
    def __add__(self, other):
        pass

    @abstractmethod
    def __sub__(self, other):
        pass

    @abstractmethod
    def __mul__(self, other):
        pass

    @abstractmethod
    def __abs__(self):
        pass

    @abstractmethod
    def __lt__(self, other) -> bool:
        pass
    
    @abstractmethod
    def __le__(self, other) -> bool:
        pass

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def __ge__(self, other) -> bool:
        pass

    @abstractmethod
    def __gt__(self, other) -> bool:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class Fraction(Ratio):

    def __init__(
        self,
        inputValue: str
    ):
        self._firstString, self._secondString = inputValue.split(':')
        self._firstNum = float(self._firstString)
        self._secondNum = float(self._secondString)
        preprocess = lambda x: str(int(float(x))) if float(x).is_integer() else str(float(x))
        self._string = f'{preprocess(self._firstString)}:{preprocess(self._secondString)}'

    @property
    def value(self):
        return self._secondNum / self._firstNum * 100

    def __add__(self, other):
        firstNum = self._firstNum
        secondNum = self._secondNum + other._secondNum
        return Fraction(f'{firstNum}:{secondNum}')

    def __sub__(self, other):
        firstNum = self._firstNum
        secondNum = self._secondNum - other._secondNum
        return Fraction(f'{firstNum}:{secondNum}')

    def __mul__(self, other: int):
        firstNum = self._firstNum
        secondNum = self._secondNum * other
        return Fraction(f'{firstNum}:{secondNum}')

    def __abs__(self):
        if self.value < 0:
            return Fraction(f'{self._firstString}:{self._secondString}'.replace('-',''))
        else:
            return self

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __str__(self):
        return self._string.replace(':','/')


class Percentage(Ratio):

    def __init__(
        self,
        inputValue: str
    ):
        self._value = float(inputValue)
        if self._value.is_integer():
            self._string = str(int(self._value))
        else:
            self._string = str(round(self._value,7))

    @property
    def value(self):
        return self._value

    def __add__(self, other):
        return Percentage(f'{self.value + other.value}')

    def __sub__(self, other):
        return Percentage(f'{self.value - other.value}')

    def __mul__(self, other: int):
        return Percentage(f'{self.value * other}')

    def __abs__(self):
        return Percentage(f'{abs(self.value)}')

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __str__(self):
        return self._string

