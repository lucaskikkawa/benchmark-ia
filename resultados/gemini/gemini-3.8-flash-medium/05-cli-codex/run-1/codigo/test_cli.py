import io
import json
import os
import subprocess
import sys
import tempfile
import pytest

import cli


def test_import_has_no_side_effects(capsys):
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_basic_word_count(tmp_path, capsys):
    f = tmp_path / "texto.txt"
    f.write_text("banana maca banana pera banana maca", encoding="utf-8")

    ret = cli.main([str(f)])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    expected = "banana\t3\nmaca\t2\npera\t1\n"
    assert captured.out == expected


def test_tie_breaking_order(tmp_path, capsys):
    f = tmp_path / "texto.txt"
    f.write_text("c b a c b a", encoding="utf-8")

    ret = cli.main([str(f)])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    expected = "a\t2\nb\t2\nc\t2\n"
    assert captured.out == expected


def test_punctuation_included_in_token(tmp_path, capsys):
    f = tmp_path / "texto.txt"
    f.write_text("Olá, olá! Olá", encoding="utf-8")

    ret = cli.main([str(f)])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    expected = "Olá\t1\nOlá,\t1\nolá!\t1\n"
    assert captured.out == expected


def test_case_fold(tmp_path, capsys):
    f = tmp_path / "texto.txt"
    f.write_text("Casa casa CASA CaSa", encoding="utf-8")

    ret = cli.main([str(f), "--ignorar-caixa"])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    expected = "casa\t4\n"
    assert captured.out == expected


def test_minimo(tmp_path, capsys):
    f = tmp_path / "texto.txt"
    f.write_text("a a a b b c", encoding="utf-8")

    ret = cli.main([str(f), "--minimo", "2"])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    expected = "a\t3\nb\t2\n"
    assert captured.out == expected


def test_top(tmp_path, capsys):
    f = tmp_path / "texto.txt"
    f.write_text("a a a a b b b c c d", encoding="utf-8")

    ret = cli.main([str(f), "--top", "2"])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    expected = "a\t4\nb\t3\n"
    assert captured.out == expected


def test_top_exceeds_results(tmp_path, capsys):
    f = tmp_path / "texto.txt"
    f.write_text("a b c", encoding="utf-8")

    ret = cli.main([str(f), "--top", "10"])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    expected = "a\t1\nb\t1\nc\t1\n"
    assert captured.out == expected


def test_minimo_and_top_combined(tmp_path, capsys):
    f = tmp_path / "texto.txt"
    f.write_text("a a a a b b b c c d", encoding="utf-8")

    # Minimo 2 leaves a(4), b(3), c(2). Top 2 takes a(4) and b(3).
    ret = cli.main([str(f), "--minimo", "2", "--top", "2"])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    expected = "a\t4\nb\t3\n"
    assert captured.out == expected


def test_json_output(tmp_path, capsys):
    f = tmp_path / "texto.txt"
    f.write_text("ação ação coração", encoding="utf-8")

    ret = cli.main([str(f), "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.endswith("\n")
    assert captured.out.count("\n") == 1
    data = json.loads(captured.out)
    assert data == [
        {"palavra": "ação", "contagem": 2},
        {"palavra": "coração", "contagem": 1},
    ]
    # Check that accents are not escaped with \u
    assert "ação" in captured.out
    assert "\\u" not in captured.out


def test_empty_results_default(tmp_path, capsys):
    f = tmp_path / "vazio.txt"
    f.write_text("", encoding="utf-8")

    ret = cli.main([str(f)])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_empty_results_json(tmp_path, capsys):
    f = tmp_path / "vazio.txt"
    f.write_text("", encoding="utf-8")

    ret = cli.main([str(f), "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.out == "[]\n"
    assert captured.err == ""


def test_filtered_to_empty_default(tmp_path, capsys):
    f = tmp_path / "texto.txt"
    f.write_text("palavra", encoding="utf-8")

    ret = cli.main([str(f), "--minimo", "5"])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_filtered_to_empty_json(tmp_path, capsys):
    f = tmp_path / "texto.txt"
    f.write_text("palavra", encoding="utf-8")

    ret = cli.main([str(f), "--minimo", "5", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.out == "[]\n"
    assert captured.err == ""


def test_unicode_composition_distinction(tmp_path, capsys):
    # Composed: \u00e9 (é), Decomposed: e\u0301 (e + combining acute)
    f = tmp_path / "unicode.txt"
    composed = "\u00e9"
    decomposed = "e\u0301"
    f.write_text(f"{composed} {decomposed}", encoding="utf-8")

    ret = cli.main([str(f)])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    # They should be counted separately
    lines = captured.out.strip().split("\n")
    assert len(lines) == 2


def test_whitespace_and_zero_width_space(tmp_path, capsys):
    f = tmp_path / "spaces.txt"
    # Non-breaking space \u00a0, formfeed \x0c, zero-width space \u200b
    content = "a\u00a0b\x0cc d\u200be"
    f.write_text(content, encoding="utf-8")

    ret = cli.main([str(f)])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    expected = "a\t1\nb\t1\nc\t1\nd\u200be\t1\n"
    assert captured.out == expected


def test_file_not_found(capsys):
    ret = cli.main(["arquivo_que_nao_existe.txt"])
    assert ret == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "Traceback" not in captured.err


def test_directory_as_file(tmp_path, capsys):
    ret = cli.main([str(tmp_path)])
    assert ret == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "Traceback" not in captured.err


def test_invalid_utf8(tmp_path, capsys):
    f = tmp_path / "invalido.bin"
    f.write_bytes(b"hello \xff\xfe world")

    ret = cli.main([str(f)])
    assert ret == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "Traceback" not in captured.err


def test_missing_required_arg(capsys):
    ret = cli.main([])
    assert ret == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "Traceback" not in captured.err


def test_unknown_flag(tmp_path, capsys):
    f = tmp_path / "texto.txt"
    f.write_text("ola", encoding="utf-8")

    ret = cli.main([str(f), "--flag-inexistente"])
    assert ret == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "Traceback" not in captured.err


@pytest.mark.parametrize(
    "invalid_val",
    ["0", "-1", "-10", "abc", "1.5", ""],
)
def test_invalid_minimo(tmp_path, capsys, invalid_val):
    f = tmp_path / "texto.txt"
    f.write_text("ola", encoding="utf-8")

    ret = cli.main([str(f), "--minimo", invalid_val])
    assert ret == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "Traceback" not in captured.err


@pytest.mark.parametrize(
    "invalid_val",
    ["0", "-1", "-10", "abc", "1.5", ""],
)
def test_invalid_top(tmp_path, capsys, invalid_val):
    f = tmp_path / "texto.txt"
    f.write_text("ola", encoding="utf-8")

    ret = cli.main([str(f), "--top", invalid_val])
    assert ret == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""
    assert "Traceback" not in captured.err


def test_help_flag(capsys):
    ret = cli.main(["--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "usage:" in captured.out
    assert captured.err == ""


def test_main_multiple_calls_no_shared_state(tmp_path, capsys):
    f1 = tmp_path / "f1.txt"
    f1.write_text("gato cachorro", encoding="utf-8")
    f2 = tmp_path / "f2.txt"
    f2.write_text("papagaio papagaio", encoding="utf-8")

    ret1 = cli.main([str(f1)])
    out1 = capsys.readouterr().out
    assert ret1 == 0
    assert "cachorro\t1\ngato\t1\n" == out1

    ret2 = cli.main([str(f2)])
    out2 = capsys.readouterr().out
    assert ret2 == 0
    assert "papagaio\t2\n" == out2


def test_large_input_100k_tokens(tmp_path, capsys):
    f = tmp_path / "large.txt"
    words = [f"word_{i % 500}" for i in range(100000)]
    f.write_text(" ".join(words), encoding="utf-8")

    ret = cli.main([str(f), "--top", "5"])
    assert ret == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    lines = captured.out.strip().split("\n")
    assert len(lines) == 5
    assert lines[0] == "word_0\t200"


def test_subprocess_execution(tmp_path):
    f = tmp_path / "texto.txt"
    f.write_text("um dois três", encoding="utf-8")

    res = subprocess.run(
        [sys.executable, "cli.py", str(f)],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert res.stdout == "dois\t1\ntrês\t1\num\t1\n"
    assert res.stderr == ""

    # Error case via subprocess
    res_err = subprocess.run(
        [sys.executable, "cli.py", "inexistente.txt"],
        capture_output=True,
        text=True,
    )
    assert res_err.returncode == 2
    assert res_err.stdout == ""
    assert res_err.stderr != ""
    assert "Traceback" not in res_err.stderr
