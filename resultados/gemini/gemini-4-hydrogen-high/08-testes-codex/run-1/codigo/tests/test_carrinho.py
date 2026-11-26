import pytest

from carrinho import calcular_total


def test_defaults_and_basic_calculation():
    assert calcular_total([]) == 0
    assert calcular_total([(1, 100)]) == 100
    assert calcular_total([(2, 150), (3, 200)]) == 900
    assert calcular_total(itens=[(4, 250)], desconto=10, frete=50) == 950


def test_return_type_is_exact_int():
    res = calcular_total([(1, 100)], desconto=10, frete=25)
    assert type(res) is int
    assert res == 115

    res_empty = calcular_total([])
    assert type(res_empty) is int
    assert res_empty == 0


def test_desconto_boundaries():
    assert calcular_total([(2, 500)], desconto=0) == 1000
    assert calcular_total([(2, 500)], desconto=100) == 0
    assert calcular_total([(2, 500)], desconto=100, frete=300) == 300
    assert calcular_total([], desconto=100, frete=300) == 0
    assert calcular_total([(0, 500)], desconto=100, frete=300) == 0


def test_desconto_truncation_down_and_float_pitfalls():
    # Exact 9.9 -> must truncate down to 9 (catches rounding, ceiling, and bruto - bruto*d//100)
    assert calcular_total([(1, 10)], desconto=1) == 9
    # Exact 0.99 -> must truncate down to 0
    assert calcular_total([(1, 1)], desconto=1) == 0
    # Exact 98.01 -> 98
    assert calcular_total([(1, 99)], desconto=1) == 98
    # Float 1000 * (1 - 29/100) == 709.9999999999999 -> int() would give 709 instead of 710
    assert calcular_total([(1, 1000)], desconto=29) == 710
    assert calcular_total([(1, 100)], desconto=7) == 93


def test_desconto_aggregate_across_lines_and_quantities():
    # Per-line truncation would give 49 + 49 = 98; aggregate gives 100 * 99 // 100 = 99
    assert calcular_total([(1, 50), (1, 50)], desconto=1) == 99
    # Same with quantity > 1 in a single line: 2 * (50 * 99 // 100) = 98 vs 99
    assert calcular_total([(2, 50)], desconto=1) == 99
    # Multiple lines with fractional remainders summing across lines: (15 + 15) * 90 // 100 = 27 vs 13 + 13 = 26
    assert calcular_total([(1, 15), (1, 15)], desconto=10) == 27
    # 3 lines of 33 with 10% discount: 99 * 90 // 100 = 89 vs 3 * (33 * 90 // 100 = 29) = 87
    assert calcular_total([(1, 33), (1, 33), (1, 33)], desconto=10) == 89


def test_frete_rules():
    # Empty cart does not pay frete
    assert calcular_total([], frete=500) == 0
    assert calcular_total([], desconto=50, frete=500) == 0

    # Zero-quantity lines do not pay frete
    assert calcular_total([(0, 100)], frete=500) == 0
    assert calcular_total([(0, 0), (0, 500)], frete=500) == 0

    # Free item with positive quantity DOES pay frete
    assert calcular_total([(1, 0)], frete=500) == 500
    assert calcular_total([(3, 0)], desconto=50, frete=500) == 500
    assert calcular_total([(0, 100), (1, 0)], frete=500) == 500

    # Frete is NOT discounted
    assert calcular_total([(1, 1000)], desconto=50, frete=200) == 700
    assert calcular_total([(0, 100), (2, 150)], desconto=10, frete=50) == 320
    assert calcular_total([(1, 0)], desconto=0, frete=0) == 0


def test_arbitrary_precision_above_2_pow_53():
    # Exceeds IEEE-754 float64 exact integer range (2**53)
    big_price = 2**53 + 1
    assert calcular_total([(1, big_price)], desconto=0, frete=1) == 2**53 + 2

    # Non-zero discount where float64 loses low bits
    bruto = (2**55 + 1) * 100 + 99
    expected = (2**55 + 1) * 99 + 98
    res = calcular_total([(1, bruto)], desconto=1, frete=7)
    assert type(res) is int
    assert res == expected + 7

    # Multiplication of large quantity and large price exceeding 2**53
    q = 10**9 + 3
    p = 10**9 + 7
    expected_big = (q * p) * (100 - 13) // 100 + 17
    assert calcular_total([(q, p)], desconto=13, frete=17) == expected_big

    # Odd value above 2**54 with 50% discount
    assert calcular_total([(1, 2**54 + 3)], desconto=50) == 2**53 + 1


@pytest.mark.parametrize(
    "itens,desconto,frete",
    [
        ([], -1, 0),
        ([], 101, 0),
        ([], 0, -1),
        ([(1, 100)], -1, 0),
        ([(1, 100)], -50, 10),
        ([(1, 100)], 101, 0),
        ([(1, 100)], 200, 10),
        ([(1, 100)], 0, -1),
        ([(1, 100)], 10, -100),
        ([(0, 100)], -1, 0),
        ([(0, 100)], 101, 0),
        ([(0, 100)], 0, -1),
        ([(-1, 0)], 0, 0),
        ([(-1, 100)], 0, 0),
        ([(0, -1)], 0, 0),
        ([(1, -1)], 0, 0),
        ([(0, 100), (-1, 100)], 0, 0),
        ([(0, 100), (1, -1)], 0, 0),
        ([(1, 100), (0, -5)], 0, 0),
        ([(1, 100), (-2, 50)], 0, 0),
        ([(1, 100), (2, -1)], 0, 0),
        ([(0, 0), (-1, 0)], 0, 0),
        ([(0, 0), (0, 0), (0, -1)], 0, 0),
        ([(-1, 500)], 100, 300),
        ([(1, -500)], 100, 300),
        ([(1, 100)], 100, -1),
    ],
)
def test_validation_raises_value_error(itens, desconto, frete):
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=desconto, frete=frete)


def test_input_list_not_mutated_on_success_or_error():
    itens_ok = [(2, 100), (0, 50), (1, 300)]
    snapshot_ok = list(itens_ok)
    assert calcular_total(itens_ok, desconto=10, frete=25) == 475
    assert itens_ok == snapshot_ok

    itens_err_item = [(0, 100), (1, -1), (2, 50)]
    snapshot_err_item = list(itens_err_item)
    with pytest.raises(ValueError):
        calcular_total(itens_err_item, desconto=10, frete=25)
    assert itens_err_item == snapshot_err_item

    itens_err_arg = [(1, 100), (2, 200)]
    snapshot_err_arg = list(itens_err_arg)
    with pytest.raises(ValueError):
        calcular_total(itens_err_arg, desconto=101, frete=10)
    assert itens_err_arg == snapshot_err_arg

    with pytest.raises(ValueError):
        calcular_total(itens_err_arg, desconto=0, frete=-1)
    assert itens_err_arg == snapshot_err_arg


def test_calls_are_independent_and_preserved_after_error():
    assert calcular_total([(2, 250)], desconto=20, frete=100) == 500

    with pytest.raises(ValueError):
        calcular_total([(1, -50)], desconto=10, frete=50)

    with pytest.raises(ValueError):
        calcular_total([(1, 100)], desconto=150, frete=50)

    with pytest.raises(ValueError):
        calcular_total([(1, 100)], desconto=10, frete=-5)

    # Subsequent calls must be unaffected by earlier valid or failing calls
    assert calcular_total([], frete=100) == 0
    assert calcular_total([(1, 100)]) == 100
    assert calcular_total([(1, 200)], desconto=10, frete=30) == 210
