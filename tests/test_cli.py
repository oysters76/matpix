import json

from matpix.cli import main


class TestNoCommand:
    def test_no_args_returns_1(self, capsys):
        result = main([])
        assert result == 1


class TestListCommand:
    def test_list_returns_0(self, capsys):
        result = main(["list"])
        assert result == 0

    def test_list_shows_all_transforms(self, capsys):
        main(["list"])
        out = capsys.readouterr().out
        expected_names = [
            "diamond",
            "flat",
            "flip_h",
            "flip_v",
            "psycho",
            "reflect",
            "rotate45",
            "scale2x",
            "squeeze",
            "trippy",
        ]
        for name in expected_names:
            assert name in out

    def test_list_json(self, capsys):
        result = main(["list", "--json"])
        assert result == 0
        data = json.loads(capsys.readouterr().out)
        assert isinstance(data, list)
        assert len(data) == 10
        for item in data:
            assert "name" in item
            assert "description" in item
            assert "matrix" in item


class TestInfoCommand:
    def test_info_returns_0(self, capsys):
        result = main(["info", "rotate45"])
        assert result == 0

    def test_info_shows_details(self, capsys):
        main(["info", "rotate45"])
        out = capsys.readouterr().out
        assert "rotate45" in out
        assert "45-degree rotation" in out
        assert "Determinant" in out

    def test_info_json(self, capsys):
        result = main(["info", "rotate45", "--json"])
        assert result == 0
        data = json.loads(capsys.readouterr().out)
        assert data["name"] == "rotate45"
        assert "description" in data
        assert "matrix" in data
        assert "determinant" in data

    def test_info_unknown_returns_1(self, capsys):
        result = main(["info", "nonexistent"])
        assert result == 1

    def test_info_unknown_json(self, capsys):
        result = main(["info", "nonexistent", "--json"])
        assert result == 1
        data = json.loads(capsys.readouterr().out)
        assert data["status"] == "error"


class TestTransformCommand:
    def test_named_transform(self, tmp_image, tmp_path, capsys, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = main(["transform", str(tmp_image), "-t", "scale2x"])
        assert result == 0
        assert (tmp_path / "transformed_test_input.png").exists()

    def test_custom_matrix(self, tmp_image, tmp_path, capsys, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = main(["transform", str(tmp_image), "-m", "1,0,0,1"])
        assert result == 0
        assert (tmp_path / "transformed_test_input.png").exists()

    def test_custom_output_path(self, tmp_image, tmp_path, capsys):
        output = tmp_path / "custom_out.png"
        result = main(["transform", str(tmp_image), "-t", "scale2x", "-o", str(output)])
        assert result == 0
        assert output.exists()

    def test_default_output_naming(self, tmp_image, tmp_path, capsys, monkeypatch):
        monkeypatch.chdir(tmp_path)
        main(["transform", str(tmp_image), "-t", "flip_h"])
        assert (tmp_path / "transformed_test_input.png").exists()

    def test_json_success_output(self, tmp_image, tmp_path, capsys):
        output = tmp_path / "json_out.png"
        result = main(
            [
                "transform",
                str(tmp_image),
                "-t",
                "rotate45",
                "-o",
                str(output),
                "--json",
            ]
        )
        assert result == 0
        data = json.loads(capsys.readouterr().out)
        assert data["status"] == "ok"
        assert data["output_file"] == str(output)
        assert data["transform"] == "rotate45"
        assert isinstance(data["matrix"], list)

    def test_missing_file_returns_1(self, capsys):
        result = main(["transform", "nonexistent.png", "-t", "rotate45"])
        assert result == 1

    def test_missing_file_stderr(self, capsys):
        main(["transform", "nonexistent.png", "-t", "rotate45"])
        err = capsys.readouterr().err
        assert "File not found" in err

    def test_missing_file_json(self, capsys):
        result = main(["transform", "nonexistent.png", "-t", "rotate45", "--json"])
        assert result == 1
        data = json.loads(capsys.readouterr().out)
        assert data["status"] == "error"
        assert "File not found" in data["message"]

    def test_unknown_transform_returns_1(self, tmp_image, capsys):
        result = main(["transform", str(tmp_image), "-t", "nonexistent"])
        assert result == 1

    def test_bad_matrix_returns_1(self, tmp_image, capsys):
        result = main(["transform", str(tmp_image), "-m", "a,b,c,d"])
        assert result == 1

    def test_bad_matrix_too_few_returns_1(self, tmp_image, capsys):
        result = main(["transform", str(tmp_image), "-m", "1,2"])
        assert result == 1

    def test_verbose_prints_to_stderr(self, tmp_image, tmp_path, capsys):
        output = tmp_path / "verbose_out.png"
        main(
            [
                "transform",
                str(tmp_image),
                "-t",
                "scale2x",
                "-o",
                str(output),
                "--verbose",
            ]
        )
        err = capsys.readouterr().err
        assert "Opened" in err
        assert "Saved to" in err

    def test_json_and_verbose_together(self, tmp_image, tmp_path, capsys):
        output = tmp_path / "both_out.png"
        result = main(
            [
                "transform",
                str(tmp_image),
                "-t",
                "flip_v",
                "-o",
                str(output),
                "--json",
                "--verbose",
            ]
        )
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["status"] == "ok"
        assert "Opened" in captured.err
