# coding: utf-8
import os
import pipes
import subprocess
import io
import asyncio
from pypeline.plugins.base import BaseAsyncPlugin


class LessPlugin(BaseAsyncPlugin):

    name = 'Less Plugin'
    description = ''

    def __init__(self, filter_pattern=r'\.less', filter_collections=None, compress=True):
        super().__init__(filter_pattern=filter_pattern, filter_collections=filter_collections)
        self.compress = compress
        self.source_path = None

    @asyncio.coroutine
    def process_file(self, path, file):
        source_path = pipes.quote('{}{}'.format(self.source_path, path))

        proc = subprocess.Popen('lessc -s{} {}'.format(' -x' if self.compress else '', source_path),
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        contents, err = proc.communicate()

        if err:
            raise Exception('Error in less processing:\n{}\n{}'.format(path, err.decode('utf-8')))

        file['contents'] = io.BytesIO(contents)

    def pre_run(self, pypeline, files):
        self.source_path = pypeline.source_path

    def post_run(self, pypeline, files):
        for path, file in files.items():
            filename, _ = os.path.splitext(path)
            pypeline.rename_file(path, '{}.css'.format(filename))
