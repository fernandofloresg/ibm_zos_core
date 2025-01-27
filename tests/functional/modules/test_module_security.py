# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from pprint import pprint
from shlex import quote
import unittest

# TODO: remove some of the logic from tests and make pytest fixtures

JCL_FILE_CONTENTS = """//HELLO    JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=S0JM
//STEP0001 EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD *
HELLO, WORLD
/*
//SYSUT2   DD SYSOUT=*
//
"""

DATA_SET_NAME = "imstestl.ims1.test05"

TEMP_PATH = "/tmp/ansible/jcl"


class ModuleSecurityTests(unittest.TestCase):
    def setUp(self):
        self.skipTest('module not tested')

    def get_exploits(self):
        exploits = []
        with open("../../helpers/shell_exploits.txt", "r") as f:
            exploits = f.read().splitlines()
        end_of_license_index = exploits.index("--end of license--") + 1
        return exploits[end_of_license_index:]

    @pytest.mark.parametrize("exploit", get_exploits())
    def test_zos_data_set_shell_injection_data_set_name(
            self, ansible_zos_module, exploit):
        hosts = ansible_zos_module
        results = hosts.all.zos_data_set(
            name=exploit, state="present", replace=True)
        for result in results.contacted.values():
            pprint(result)
            assert "ValueError" in result.get("msg")

    @pytest.mark.parametrize("exploit", get_exploits())
    def test_zos_data_set_shell_injection_data_set_member_name(self, ansible_zos_module, exploit):
        hosts = ansible_zos_module
        results = hosts.all.zos_data_set(
            name=exploit, state="present", type="member", replace=True
        )
        for result in results.contacted.values():
            pprint(result)
            assert "ValueError" in result.get("msg")

    def test_job_submit_shell_injection_data_set_volume(self, ansible_zos_module):
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(
                quote(JCL_FILE_CONTENTS), TEMP_PATH)
        )
        hosts.all.zos_data_set(
            name=DATA_SET_NAME, state="present", type="pds", replace=True
        )
        hosts.all.shell(
            cmd="cp {0}/SAMPLE \"//'{1}(SAMPLE)'\"".format(TEMP_PATH,
                                                           DATA_SET_NAME)
        )
        all_results = []
        for exploit in self.get_exploits():
            results = hosts.all.zos_job_submit(
                src="{0}(SAMPLE)".format(DATA_SET_NAME),
                location="DATA_SET",
                volume=exploit,
                wait=True,
            )
            all_results.append(results)
        hosts.all.file(path=TEMP_PATH, state="absent")
        for results in all_results:
            for result in results.contacted.values():
                pprint(result)
                assert "ValueError" in result.get("module_stderr")

    def test_job_submit_shell_injection_data_set_name(self, ansible_zos_module):
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(
                quote(JCL_FILE_CONTENTS), TEMP_PATH)
        )
        hosts.all.zos_data_set(
            name=DATA_SET_NAME, state="present", type="pds", replace=True
        )
        hosts.all.shell(
            cmd="cp {0}/SAMPLE \"//'{1}(SAMPLE)'\"".format(TEMP_PATH,
                                                           DATA_SET_NAME)
        )
        all_results = []
        for exploit in self.get_exploits():
            results = hosts.all.zos_job_submit(
                src="{0}".format(exploit), location="DATA_SET", wait=True
            )
            all_results.append(results)
        hosts.all.file(path=TEMP_PATH, state="absent")
        for results in all_results:
            for result in results.contacted.values():
                pprint(result)
                assert "ValueError" in result.get("module_stderr")

    def test_job_submit_shell_injection_uss(self, ansible_zos_module):
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(
                quote(JCL_FILE_CONTENTS), TEMP_PATH)
        )
        all_results = []
        for exploit in self.get_exploits():
            results = hosts.all.zos_job_submit(
                src="{0}".format(exploit), location="USS", wait=True
            )
            all_results.append(results)
        hosts.all.file(path=TEMP_PATH, state="absent")
        for results in all_results:
            for result in results.contacted.values():
                pprint(result)
                assert "ValueError" in result.get("module_stderr")

    @pytest.mark.parametrize("exploit", get_exploits())
    def test_zos_job_output_shell_injection_job_id(self, ansible_zos_module, exploit):
        hosts = ansible_zos_module
        results = hosts.all.zos_job_output(job_id=exploit)
        for result in results.contacted.values():
            pprint(result)
            assert "ValueError" in result.get("msg")

    @pytest.mark.parametrize("exploit", get_exploits())
    def test_zos_job_output_shell_injection_owner(self, ansible_zos_module, exploit):
        hosts = ansible_zos_module
        results = hosts.all.zos_job_output(owner=exploit)
        for result in results.contacted.values():
            pprint(result)
            assert "ValueError" in result.get("msg")

    @pytest.mark.parametrize("exploit", get_exploits())
    def test_zos_job_output_shell_injection_job_name(self, ansible_zos_module, exploit):
        hosts = ansible_zos_module
        results = hosts.all.zos_job_output(job_name=exploit)
        for result in results.contacted.values():
            pprint(result)
            assert "ValueError" in result.get("msg")

    @pytest.mark.parametrize("exploit", get_exploits())
    def test_zos_job_output_shell_injection_dd_name(self, ansible_zos_module, exploit):
        hosts = ansible_zos_module
        results = hosts.all.zos_job_output(owner="omvsadm", ddname=exploit)
        for result in results.contacted.values():
            pprint(result)
            assert "ValueError" in result.get("msg")
