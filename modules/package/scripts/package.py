#!/usr/bin/env python
#
# Python because it comes on Mac and Linux - Node must be installed.
#

import sys
import os
import os.path
import json
import shutil
import hashlib
import base64
import tempfile
import zipfile

class Sandbox:
    '''
    A temporary directory for staging a lambda package.

    We import files, write new files, and run commands in the Sandbox to
    produce the image we want to zip for the lambda.
    '''
    FILE_STRING_MTIME = 1493649512

    def __init__(self):
        self.dir = tempfile.mkdtemp(suffix = 'lambda-packager')

    def run_command(self, cmd):
        cwd = os.getcwd()
        os.chdir(self.dir)
        result = os.system(cmd)
        os.chdir(cwd)
        return result

    def import_path(self, path):
        if os.path.isdir(path):
            shutil.copytree(path, os.path.join(self.dir, os.path.basename(path)))
        else:
            shutil.copy2(path, self.dir)

    def add_file_string(self, path, contents):
        full_path = os.path.join(self.dir, path)
        with open(full_path, 'w') as f:
            f.write(contents)
        os.utime(full_path, (self.FILE_STRING_MTIME, self.FILE_STRING_MTIME))

    def _files_visit(self, result, dirname, names):
        for name in names:
            src = os.path.join(dirname, name)
            if dirname == self.dir:
                dst = name
            else:
                dst = os.path.join(dirname[len(self.dir)+1:], name)
            result.append(dst)

    def files(self):
        result = []
        os.path.walk(self.dir, self._files_visit, result)
        return result

    def zip(self, output_path):
        zf = zipfile.ZipFile(output_path, 'w')
        for filename in self.files():
            zf.write(os.path.join(self.dir, filename), filename)
        zf.close()

    def delete(self):
        try:
            shutil.rmtree(self.dir)
        except:
            pass


class SandboxMtimeDecorator:
    '''A decorator for Sandbox which sets all files newly created by some command to `mtime'.'''
    def __init__(self, sb, mtime):
        self.sb = sb
        self.mtime = mtime
        self.before_files = set(self.sb.files())

    def __getattr__(self, name):
        return getattr(self.sb, name)

    def run_command(self, cmd):
        self.sb.run_command(cmd)
        for filename in set(self.sb.files()).difference(self.before_files):
            os.utime(os.path.join(self.sb.dir, filename), (self.mtime, self.mtime))

class RequirementsCollector:
    def __init__(self, path):
        self.path = path

    def _source_path(self):
        return os.path.join(os.getcwd(), os.path.dirname(self.path))

    def _source_requirements_file(self):
        return os.path.join(self._source_path(), self._requirements_file())

    def _requirements_mtime(self):
        return os.stat(self._source_requirements_file()).st_mtime

    @staticmethod
    def collector(path):
        path_type = os.path.splitext(path)[1]
        if path_type == '.py':
            return PythonRequirementsCollector(path)
        elif path_type == '.js':
            return NodeRequirementsCollector(path)
        elif path_type == '':
            return DirectoryRequirementsCollector(path)
        else:
            raise Exception("Unknown path type '{}'".format(path_type))

class PythonRequirementsCollector(RequirementsCollector):
    def _requirements_file(self):
        return 'requirements.txt'

    def collect(self, sb):
        requirements_file = self._source_requirements_file()
        if not os.path.isfile(requirements_file):
            return
        mtime = self._requirements_mtime()
        sb.add_file_string('setup.cfg', "[install]\nprefix=\n")
        sbm = SandboxMtimeDecorator(sb, mtime)
        sbm.run_command('pip install -r {} -t {}/ >/dev/null'.format(requirements_file, sb.dir))
        sbm.run_command('python -c \'import time, compileall; time.time = lambda: {}; compileall.compile_dir(".", force=True)\' >/dev/null'.format(mtime))

class NodeRequirementsCollector(RequirementsCollector):
    def _requirements_file(self):
        return 'package.json'

    def collect(self, sb):
        requirements_file = self._source_requirements_file()
        if not os.path.isfile(requirements_file):
            return
        sb.import_path(self._source_requirements_file())
        sbm = SandboxMtimeDecorator(sb, self._requirements_mtime())
        sbm.run_command('npm install --production >/dev/null 2>&1')
        for filename in sbm.files():
            if not filename.endswith('package.json'):
                continue
            full_path = os.path.join(sbm.dir, filename)
            mtime = os.stat(full_path).st_mtime
            with open(full_path, 'rb') as f:
                contents = f.read()
            contents = contents.replace(str(sb.dir), '/tmp/lambda-package')
            with open(full_path, 'wb') as f:
                f.write(contents)
            os.utime(full_path, (mtime, mtime))

class DirectoryRequirementsCollector(RequirementsCollector):
    def _requirements_file(self):
        return ''

    def collect(self, sb):
        pass

class Packager:
    def __init__(self, input_values):
        self.input = input_values
        self.path = self.input["path"]
        self.include_paths = []
        if len(self.input.get('include_paths', '')) > 0:
            self.include_paths = self.input['include_paths'].split(',')

    def output_path(self):
        if self.input.get('output_path', '') != '':
            return self.input['output_path']
        return os.path.splitext(self.path)[0] + ".zip"
    
    def output_size(self):
        return str(os.path.getsize(self.output_path()))

    def paths_to_import(self):
        yield self.path
        source_dir = os.path.dirname(self.path)
        for include_path in self.include_paths:
            yield os.path.join(source_dir, include_path)

    def package(self):
        sb = Sandbox()
        for path in self.paths_to_import():
            sb.import_path(path)
        RequirementsCollector.collector(self.path).collect(sb)
        sb.zip(self.output_path())
        sb.delete()

    def output_base64sha256(self):
        with open(self.output_path(), 'r') as f:
            contents = f.read()
        return base64.b64encode(hashlib.sha256(contents).digest())

    def output(self):
        return {
          "path": self.path,
          "output_path": self.output_path(),
          "output_size": self.output_size(),
          "output_base64sha256": self.output_base64sha256()
        }

def main():
    packager = Packager(json.load(sys.stdin))
    packager.package()
    json.dump(packager.output(), sys.stdout)

if __name__=='__main__':
    main()
