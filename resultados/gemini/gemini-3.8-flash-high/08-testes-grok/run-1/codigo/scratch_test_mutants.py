import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

BASE_DESCONTOS = Path("/tmp/bench-q34eta46/descontos.py").read_text()
TESTS_DIR = Path("/tmp/bench-q34eta46/tests")

mutants = {}

# Mutant 1: preco bool allowed
mutants["preco_bool_allowed"] = BASE_DESCONTOS.replace(
    'if isinstance(preco_centavos, bool) or not isinstance(preco_centavos, int):',
    'if not isinstance(preco_centavos, int):'
)

# Mutant 2: preco float allowed
mutants["preco_float_allowed"] = BASE_DESCONTOS.replace(
    'if isinstance(preco_centavos, bool) or not isinstance(preco_centavos, int):',
    'if isinstance(preco_centavos, bool) or not isinstance(preco_centavos, (int, float)):\n        pass\n    preco_centavos = int(preco_centavos)\n    if False:'
)

# Mutant 3: preco negative allowed
mutants["preco_negative_allowed"] = BASE_DESCONTOS.replace(
    'if preco_centavos < 0:\n        raise ValueError("preco negativo")',
    '# no negative check'
)

# Mutant 4: preco negative raises TypeError
mutants["preco_negative_raises_type_error"] = BASE_DESCONTOS.replace(
    'if preco_centavos < 0:\n        raise ValueError("preco negativo")',
    'if preco_centavos < 0:\n        raise TypeError("preco negativo")'
)

# Mutant 5: preco 0 disallowed
mutants["preco_zero_disallowed"] = BASE_DESCONTOS.replace(
    'if preco_centavos < 0:',
    'if preco_centavos <= 0:'
)

# Mutant 6: cupom type error raises ValueError
mutants["cupom_type_raises_value_error"] = BASE_DESCONTOS.replace(
    'if cupom is not None and not isinstance(cupom, str):\n        raise TypeError("cupom deve ser str ou None")',
    'if cupom is not None and not isinstance(cupom, str):\n        raise ValueError("cupom deve ser str ou None")'
)

# Mutant 7: cupom strip
mutants["cupom_strip"] = BASE_DESCONTOS.replace(
    'final, aplicado = _aplicar(preco_centavos, cupom, dia)',
    'final, aplicado = _aplicar(preco_centavos, cupom.strip() if isinstance(cupom, str) else cupom, dia)'
)

# Mutant 8: cupom upper
mutants["cupom_upper"] = BASE_DESCONTOS.replace(
    'final, aplicado = _aplicar(preco_centavos, cupom, dia)',
    'final, aplicado = _aplicar(preco_centavos, cupom.upper() if isinstance(cupom, str) else cupom, dia)'
)

# Mutant 9: cupom whitespace allowed as empty
mutants["cupom_whitespace_allowed"] = BASE_DESCONTOS.replace(
    'if cupom is None or cupom == "":',
    'if cupom is None or cupom.strip() == "":'
)

# Mutant 10: cupom empty string raises ValueError
mutants["cupom_empty_raises_value_error"] = BASE_DESCONTOS.replace(
    'if cupom is None or cupom == "":',
    'if cupom is None:\n        return preco, None\n    if cupom == "":\n        raise ValueError("vazio")\n    if False:'
)

# Mutant 11: cupom empty returns cupom_aplicado=""
mutants["cupom_empty_returns_empty_string"] = BASE_DESCONTOS.replace(
    'if cupom is None or cupom == "":\n        return preco, None',
    'if cupom is None:\n        return preco, None\n    if cupom == "":\n        return preco, ""'
)

# Mutant 12: cupom None raises TypeError
mutants["cupom_none_raises_type_error"] = BASE_DESCONTOS.replace(
    'if cupom is not None and not isinstance(cupom, str):',
    'if not isinstance(cupom, str):'
)

# Mutant 13: cupom unknown returns no discount instead of ValueError
mutants["cupom_unknown_no_discount"] = BASE_DESCONTOS.replace(
    'raise ValueError("cupom desconhecido")',
    'return preco, None'
)

# Mutant 14: hoje non-str raises ValueError instead of TypeError
mutants["hoje_type_raises_value_error"] = BASE_DESCONTOS.replace(
    'if not isinstance(hoje, str):\n        raise TypeError("hoje deve ser str")',
    'if not isinstance(hoje, str):\n        raise ValueError("hoje deve ser str")'
)

# Mutant 15: hoje format len/hyphen check omitted
mutants["hoje_format_check_omitted"] = BASE_DESCONTOS.replace(
    'if len(hoje) != 10 or hoje[4] != "-" or hoje[7] != "-":\n        raise ValueError("data invalida")',
    '# format check omitted'
)

# Mutant 16: OFF10 uses preco - preco // 10
mutants["off10_preco_minus_div10"] = BASE_DESCONTOS.replace(
    'return (preco * 90) // 100, cupom',
    'return preco - preco // 10, cupom'
)

# Mutant 17: OFF10 uses preco - (preco * 10) // 100
mutants["off10_preco_minus_mult10"] = BASE_DESCONTOS.replace(
    'return (preco * 90) // 100, cupom',
    'return preco - (preco * 10) // 100, cupom'
)

# Mutant 18: OFF10 preco 0 gives cupom_aplicado None
mutants["off10_preco0_none"] = BASE_DESCONTOS.replace(
    'if cupom == "OFF10":\n        return (preco * 90) // 100, cupom',
    'if cupom == "OFF10":\n        return ((preco * 90) // 100, cupom) if preco > 0 else (0, None)'
)

# Mutant 19: OFF5 uses preco - (preco * 5) // 100
mutants["off5_preco_minus_mult5"] = BASE_DESCONTOS.replace(
    'return (preco * 95) // 100, cupom',
    'return preco - (preco * 5) // 100, cupom'
)

# Mutant 20: OFF5 uses preco - preco // 20
mutants["off5_preco_minus_div20"] = BASE_DESCONTOS.replace(
    'return (preco * 95) // 100, cupom',
    'return preco - preco // 20, cupom'
)

# Mutant 21: FIXO500 no floor 0
mutants["fixo500_no_floor"] = BASE_DESCONTOS.replace(
    'return max(0, preco - 500), cupom',
    'return preco - 500, cupom'
)

# Mutant 22: FIXO500 desconto always 500
mutants["fixo500_desconto_always_500"] = BASE_DESCONTOS.replace(
    '"desconto": preco_centavos - final,',
    '"desconto": 500 if cupom == "FIXO500" else preco_centavos - final,'
)

# Mutant 23: FIXO500 cupom_aplicado None if preco <= 500
mutants["fixo500_none_when_under_500"] = BASE_DESCONTOS.replace(
    'return max(0, preco - 500), cupom',
    'return (max(0, preco - 500), cupom) if preco > 500 else (0, None)'
)

# Mutant 24: FIXO500 subtracts 50 instead of 500
mutants["fixo500_subtract_50"] = BASE_DESCONTOS.replace(
    'return max(0, preco - 500), cupom',
    'return max(0, preco - 50), cupom'
)

# Mutant 25: BEMVINDO uses preco - (preco * 20) // 100
mutants["bemvindo_preco_minus_mult20"] = BASE_DESCONTOS.replace(
    'return (preco * 80) // 100, cupom',
    'return preco - (preco * 20) // 100, cupom'
)

# Mutant 26: BEMVINDO start excluded (inicio < dia <= fim)
mutants["bemvindo_start_excluded"] = BASE_DESCONTOS.replace(
    'if inicio <= dia <= fim:',
    'if inicio < dia <= fim:'
)

# Mutant 27: BEMVINDO end excluded (inicio <= dia < fim)
mutants["bemvindo_end_excluded"] = BASE_DESCONTOS.replace(
    'if inicio <= dia <= fim:',
    'if inicio <= dia < fim:'
)

# Mutant 28: BEMVINDO includes 2023-12-31
mutants["bemvindo_includes_2023_12_31"] = BASE_DESCONTOS.replace(
    'inicio = date(2024, 1, 1)',
    'inicio = date(2023, 12, 31)'
)

# Mutant 29: BEMVINDO includes 2025-01-01
mutants["bemvindo_includes_2025_01_01"] = BASE_DESCONTOS.replace(
    'fim = date(2024, 12, 31)',
    'fim = date(2025, 1, 1)'
)

# Mutant 30: BEMVINDO outside window raises ValueError
mutants["bemvindo_outside_raises_error"] = BASE_DESCONTOS.replace(
    'if inicio <= dia <= fim:\n            return (preco * 80) // 100, cupom\n        return preco, None',
    'if inicio <= dia <= fim:\n            return (preco * 80) // 100, cupom\n        raise ValueError("fora da janela")'
)

# Mutant 31: BEMVINDO outside window sets cupom_aplicado = "BEMVINDO"
mutants["bemvindo_outside_sets_cupom"] = BASE_DESCONTOS.replace(
    'if inicio <= dia <= fim:\n            return (preco * 80) // 100, cupom\n        return preco, None',
    'if inicio <= dia <= fim:\n            return (preco * 80) // 100, cupom\n        return preco, cupom'
)

# Mutant 32: NATAL uses preco - (preco * 15) // 100
mutants["natal_preco_minus_mult15"] = BASE_DESCONTOS.replace(
    'return (preco * 85) // 100, cupom',
    'return preco - (preco * 15) // 100, cupom'
)

# Mutant 33: NATAL only on 25
mutants["natal_only_25"] = BASE_DESCONTOS.replace(
    'if (dia.month, dia.day) in {(12, 24), (12, 25)}:',
    'if (dia.month, dia.day) in {(12, 25)}:'
)

# Mutant 34: NATAL only on 24
mutants["natal_only_24"] = BASE_DESCONTOS.replace(
    'if (dia.month, dia.day) in {(12, 24), (12, 25)}:',
    'if (dia.month, dia.day) in {(12, 24)}:'
)

# Mutant 35: NATAL only in year 2024
mutants["natal_only_2024"] = BASE_DESCONTOS.replace(
    'if (dia.month, dia.day) in {(12, 24), (12, 25)}:',
    'if dia.year == 2024 and (dia.month, dia.day) in {(12, 24), (12, 25)}:'
)

# Mutant 36: NATAL also on 23
mutants["natal_also_23"] = BASE_DESCONTOS.replace(
    'if (dia.month, dia.day) in {(12, 24), (12, 25)}:',
    'if (dia.month, dia.day) in {(12, 23), (12, 24), (12, 25)}:'
)

# Mutant 37: NATAL also on 26
mutants["natal_also_26"] = BASE_DESCONTOS.replace(
    'if (dia.month, dia.day) in {(12, 24), (12, 25)}:',
    'if (dia.month, dia.day) in {(12, 24), (12, 25), (12, 26)}:'
)

# Mutant 38: NATAL on any month (dia.day in {24, 25})
mutants["natal_any_month"] = BASE_DESCONTOS.replace(
    'if (dia.month, dia.day) in {(12, 24), (12, 25)}:',
    'if dia.day in {24, 25}:'
)

# Mutant 39: NATAL outside raises ValueError
mutants["natal_outside_raises_error"] = BASE_DESCONTOS.replace(
    'if (dia.month, dia.day) in {(12, 24), (12, 25)}:\n            return (preco * 85) // 100, cupom\n        return preco, None',
    'if (dia.month, dia.day) in {(12, 24), (12, 25)}:\n            return (preco * 85) // 100, cupom\n        raise ValueError("nao e natal")'
)

# Mutant 40: Return preco_final as float
mutants["return_float_preco_final"] = BASE_DESCONTOS.replace(
    '"preco_final": final,',
    '"preco_final": float(final),'
)

# Mutant 41: Return desconto as float
mutants["return_float_desconto"] = BASE_DESCONTOS.replace(
    '"desconto": preco_centavos - final,',
    '"desconto": float(preco_centavos - final),'
)

# Mutant 42: Return extra key
mutants["return_extra_key"] = BASE_DESCONTOS.replace(
    '"cupom_aplicado": aplicado,\n    }',
    '"cupom_aplicado": aplicado,\n        "status": "ok",\n    }'
)

# Mutant 43: Return wrong key name
mutants["return_wrong_key"] = BASE_DESCONTOS.replace(
    '"preco_final": final,',
    '"final": final,'
)

print(f"Total mutants defined: {len(mutants)}")

all_passed = True
for name, code in mutants.items():
    if code == BASE_DESCONTOS:
        print(f"WARNING: Mutant {name} was not properly created (same as base)!")
        all_passed = False
        continue

    with tempfile.TemporaryDirectory() as tmpdir:
        # Write mutant descontos.py
        with open(os.path.join(tmpdir, "descontos.py"), "w") as f:
            f.write(code)
        # Copy tests dir
        shutil.copytree(TESTS_DIR, os.path.join(tmpdir, "tests"))
        # Run pytest
        res = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_descontos.py"],
            cwd=tmpdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if res.returncode == 0:
            print(f"FAILED TO KILL MUTANT: {name}")
            all_passed = False
        else:
            print(f"Killed mutant: {name}")

if all_passed:
    print("\nSUCCESS! All mutants were killed by the test suite!")
else:
    print("\nFAILURE! Some mutants survived!")
