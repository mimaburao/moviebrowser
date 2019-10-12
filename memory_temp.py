#memory_tempfileを使う場合
#必ず初期化後、インスタンスでメソッドを用いる
from memory_tempfile import __version__


def test_version():
    assert __version__ == '0.1.0'


def example1():
    from memory_tempfile import MemoryTempfile

    tempfile = MemoryTempfile()
    print(tempfile.fallback)
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as td:
        print(td.name)
        pass

example1()
