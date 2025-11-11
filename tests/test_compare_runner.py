import os
import shutil
import runpy
from pathlib import Path


def test_write_summary_md_runs(tmp_path, monkeypatch):
    # Create a temporary project layout with data/ and scripts/
    project = tmp_path
    data_dir = project / 'data'
    data_dir.mkdir()

    # Copy fixtures into data/
    base = Path(__file__).parent / 'fixtures'
    for fname in ['benin_small.csv', 'togo_small.csv', 'sierraleone_small.csv']:
        # write fixtures as the expected cleaned filenames
        dst_name = fname.replace('_small', '_clean')
        shutil.copy(base / fname, data_dir / dst_name)

    # Copy the writer script into tmp project
    src_script = Path(__file__).parents[1] / 'scripts' / 'write_summary_md.py'
    dst_script = project / 'scripts'
    dst_script.mkdir()
    shutil.copy(src_script, dst_script / 'write_summary_md.py')

    # Run the writer with cwd set to project (it will read data/ and write outputs/compare/summary_table.md)
    monkeypatch.chdir(project)
    runpy.run_path(str(dst_script / 'write_summary_md.py'), run_name='__main__')

    out_file = project / 'outputs' / 'compare' / 'summary_table.md'
    assert out_file.exists(), 'summary_table.md should be created'

    content = out_file.read_text(encoding='utf-8')
    assert 'ANOVA:' in content
    assert 'Kruskal' in content
    assert 'Average GHI ranking' in content
