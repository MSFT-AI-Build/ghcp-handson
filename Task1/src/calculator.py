"""
간단한 계산기 모듈
GitHub Copilot Chat - Agent Mode를 활용하여 각 함수의 구현을 완성하세요.
"""


def add(a: float, b: float) -> float:
    """두 수의 합을 반환합니다."""
    pass


def subtract(a: float, b: float) -> float:
    """두 수의 차를 반환합니다."""
    pass


def multiply(a: float, b: float) -> float:
    """두 수의 곱을 반환합니다."""
    pass


def divide(a: float, b: float) -> float:
    """두 수의 나눗셈 결과를 반환합니다. 0으로 나누면 ValueError를 발생시킵니다."""
    pass


def power(base: float, exponent: float) -> float:
    """거듭제곱 결과를 반환합니다."""
    pass


def modulo(a: float, b: float) -> float:
    """나머지 연산 결과를 반환합니다. 0으로 나누면 ValueError를 발생시킵니다."""
    pass


def square_root(a: float) -> float:
    """제곱근을 반환합니다. 음수이면 ValueError를 발생시킵니다."""
    pass


def factorial(n: int) -> int:
    """팩토리얼을 반환합니다. 음수이면 ValueError를 발생시킵니다."""
    pass


if __name__ == "__main__":
    print("=== 계산기 테스트 ===")
    print(f"add(2, 3) = {add(2, 3)}")
    print(f"subtract(10, 4) = {subtract(10, 4)}")
    print(f"multiply(3, 5) = {multiply(3, 5)}")
    print(f"divide(10, 3) = {divide(10, 3)}")
    print(f"power(2, 8) = {power(2, 8)}")
    print(f"modulo(10, 3) = {modulo(10, 3)}")
    print(f"square_root(16) = {square_root(16)}")
    print(f"factorial(5) = {factorial(5)}")
