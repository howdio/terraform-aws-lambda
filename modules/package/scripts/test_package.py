import unittest
import package
import zipfile
import time

import os #FIXME

def do(input_values):
    if not input_values.has_key("output_path"):
        input_values["output_path"] = ""
    if not input_values.has_key("include_paths"):
        input_values["include_paths"] = ''
    p = package.Packager(input_values)
    p.package()
    output = p.output()
    zf = zipfile.ZipFile(output["output_path"], 'r')
    zip_contents = {}
    for name in zf.namelist():
        zip_contents[name] = zf.read(name)
    zf.close()
    return {
        "output": output,
        "zip_contents": zip_contents
    }

class TestPackager(unittest.TestCase):
    def test_packages_a_python_directory(self):
        result = do({"path": "test/python-simple"})
        self.assertEquals(result["zip_contents"]["python-simple/foo.py"], "# Hello, Python!\n")

    def test_packages_a_python_script_with_no_dependencies(self):
        result = do({"path": "test/python-simple/foo.py"})
        self.assertEquals(result["zip_contents"]["foo.py"], "# Hello, Python!\n")

    def test_packaging_source_without_dependencies_twice_produces_the_same_hash(self):
        result1 = do({"path": "test/python-simple/foo.py"})
        time.sleep(2) # Allow for current time to "infect" result
        result2 = do({"path": "test/python-simple/foo.py"})
        self.assertEquals(result1["output"]["output_base64sha256"], result2["output"]["output_base64sha256"])

    def test_uses_specified_output_filename(self):
        result = do({
            "path": "test/python-simple/foo.py",
            "output_path": "test/foo-x.zip"
        })
        self.assertEquals(result["output"]["output_path"], "test/foo-x.zip")

    def test_packages_extra_files(self):
        result = do({
            "path": "test/python-simple/foo.py",
            "include_paths": "extra.txt"
        })
        self.assertEquals(result["zip_contents"]["extra.txt"], "Extra File!\n")

    def test_packages_extra_directories(self):
        result = do({
            "path": "test/python-simple/foo.py",
            "include_paths": "extra.txt,extra-dir"
        })
        self.assertEquals(result["zip_contents"]["extra-dir/dir.txt"], "Dir File!\n")

    def test_installs_python_requirements(self):
        result = do({"path": "test/python-deps/foo.py"})
        self.assertTrue(result["zip_contents"].has_key("mock/__init__.py"))

    def test_packaging_python_with_requirements_twice_produces_the_same_hsah(self):
        result1 = do({"path": "test/python-deps/foo.py"})
        time.sleep(2) # Allow for current time to "infect" result
        result2 = do({"path": "test/python-deps/foo.py"})
        self.assertEquals(result1["output"]["output_base64sha256"], result2["output"]["output_base64sha256"])

    def test_packages_a_node_script_with_no_dependencies(self):
        result = do({"path": "test/node-simple/foo.js"})
        self.assertEquals(result["zip_contents"]["foo.js"], "// Hello, Node!\n")

    def test_packages_a_node_script_with_dependencies(self):
        result = do({"path": "test/node-deps/foo.js"})
        self.assertTrue(result["zip_contents"].has_key("node_modules/"))
        self.assertTrue(result["zip_contents"].has_key("node_modules/uuid/"))

    def test_packaging_node_with_dependencies_twice_produces_same_hash(self):
        result1 = do({"path": "test/node-deps/foo.js"})
        os.system("cp test/node-deps/foo.zip /tmp/a.zip")
        time.sleep(2) # Allow for current time to "infect" result
        result2 = do({"path": "test/node-deps/foo.js"})
        os.system("cp test/node-deps/foo.zip /tmp/b.zip")
        self.assertEquals(result1["output"]["output_base64sha256"], result2["output"]["output_base64sha256"])
