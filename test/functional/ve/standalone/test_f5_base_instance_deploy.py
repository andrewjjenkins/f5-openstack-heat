# Copyright 2015-2016 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

from f5.bigip import BigIP
import os
import pytest
import time


BIGIP_11_5_4_IMG = 'BIGIP-11.5.4.0.0.256'
BIGIP_11_5_4_VERSION = '11.5.4'
BIGIP_11_6_IMG = 'BIGIP-11.6.0.0.0.401'
BIGIP_11_6_VERSION = '11.6.0'
BIGIP_12_0_IMG = 'BIGIP-12.0.0.0.0.606'
BIGIP_12_0_VERSION = '12.0.0'

# At the very minimum, these should be created
EXPECTED_IFC_NAMES = ['1.1', 'mgmt']
EXPECTED_SELFIP_NAMES = [u'selfip.network-1.1']
EXPECTED_VLAN_NAMES = [u'network-1.1']


def get_floating_ip_output(stack):
    for output in stack.outputs:
        if 'floating_ip' == output['output_key']:
            return output['output_value']


def wait_for_active_licensed_bigip(
        bigip_ip, username, password, bigip_version, ifc_num
):
    # We can hide this later and refine the values
    max_attempts = 50
    interval = 10
    # This thing is going to take at least a minute to get networking up
    time.sleep(60)
    bigip = BigIP(bigip_ip, username, password)
    for attempt in range(max_attempts):
        time.sleep(interval)
        try:
            registration = bigip.shared.licensing.registration.load()
            assert registration.licensedVersion == bigip_version
            assert len(bigip.net.vlans.get_collection()) == ifc_num - 1
            assert len(bigip.net.interfaces.get_collection()) == ifc_num
            assert len(bigip.net.selfips.get_collection()) == ifc_num - 1
            return bigip
        except Exception:
            continue
    pytest.fail('Too many attempts made to contact the BigIP. Failing...')


def check_net_components(bigip, ifc_num):
    expected_ifc_names = EXPECTED_IFC_NAMES[:]
    expected_selfip_names = EXPECTED_SELFIP_NAMES[:]
    expected_vlan_names = EXPECTED_VLAN_NAMES[:]
    for ifc in range(2, ifc_num):
        expected_ifc_names.append('1.{}'.format(ifc))
        expected_selfip_names.append(u'selfip.network-1.{}'.format(ifc))
        expected_vlan_names.append(u'network-1.{}'.format(ifc))
    ifcs = bigip.net.interfaces.get_collection()
    ifc_names = [ifc.name for ifc in ifcs]
    assert sorted(expected_ifc_names) == sorted(ifc_names)
    selfips = bigip.net.selfips.get_collection()
    selfip_names = [selfip.name for selfip in selfips]
    assert sorted(expected_selfip_names) == sorted(selfip_names)
    vlans = bigip.net.vlans.get_collection()
    vlan_names = [vlan.name for vlan in vlans]
    assert sorted(expected_vlan_names) == sorted(vlan_names)


@pytest.fixture
def CommonTemplateDir(SupportedDir):
    return os.path.join(
        os.path.join(
            SupportedDir, 've', 'standalone'
        )
    )


# These tests require a patched VE instance in your stack

def test_f5_base_instance_deploy_2_nic_11_5_4(
        HeatStack, symbols, CommonTemplateDir
):
    hc, stack = HeatStack(
        os.path.join(CommonTemplateDir, 'f5_ve_standalone_2_nic.yaml'),
        'func_test_standalone_2_nic',
        parameters={
            've_image': BIGIP_11_5_4_IMG,
            'external_network': 'external_network',
            'mgmt_network': 'mgmt_net',
            've_flavor': 'm1.xlarge',
            'network_1': 'data1_net',
            'f5_ve_os_ssh_key': 'testlab',
            'admin_password': symbols.bigip_admin_password,
            'root_password': symbols.bigip_root_password,
            'license': symbols.license
        }
    )
    updated_stack = hc.stacks.get(stack.id)
    floating_ip = get_floating_ip_output(updated_stack)
    bigip = wait_for_active_licensed_bigip(
        floating_ip, 'admin', symbols.bigip_admin_password,
        BIGIP_11_5_4_VERSION, 2
    )
    check_net_components(bigip, 2)


def test_f5_base_instance_deploy_2_nic_11_6(
        HeatStack, symbols, CommonTemplateDir
):
    hc, stack = HeatStack(
        os.path.join(CommonTemplateDir, 'f5_ve_standalone_2_nic.yaml'),
        'func_test_standalone_2_nic',
        parameters={
            've_image': BIGIP_11_6_IMG,
            'external_network': 'external_network',
            'mgmt_network': 'mgmt_net',
            'network_1': 'data1_net',
            'f5_ve_os_ssh_key': 'testlab',
            'admin_password': symbols.bigip_admin_password,
            'root_password': symbols.bigip_root_password,
            'license': symbols.license
        }
    )
    updated_stack = hc.stacks.get(stack.id)
    floating_ip = get_floating_ip_output(updated_stack)
    bigip = wait_for_active_licensed_bigip(
        floating_ip, 'admin', symbols.bigip_admin_password,
        BIGIP_11_6_VERSION, 2
    )
    check_net_components(bigip, 2)


def test_f5_base_instance_deploy_2_nic_12_0(
        HeatStack, symbols, CommonTemplateDir
):
    hc, stack = HeatStack(
        os.path.join(CommonTemplateDir, 'f5_ve_standalone_2_nic.yaml'),
        'func_test_standalone_2_nic',
        parameters={
            've_image': BIGIP_12_0_IMG,
            'external_network': 'external_network',
            'mgmt_network': 'mgmt_net',
            'network_1': 'data1_net',
            'f5_ve_os_ssh_key': 'testlab',
            'admin_password': symbols.bigip_admin_password,
            'root_password': symbols.bigip_root_password,
            'license': symbols.license
        }
    )
    updated_stack = hc.stacks.get(stack.id)
    floating_ip = get_floating_ip_output(updated_stack)
    bigip = wait_for_active_licensed_bigip(
        floating_ip, 'admin', symbols.bigip_admin_password,
        BIGIP_12_0_VERSION, 2
    )
    check_net_components(bigip, 2)


def test_f5_base_instance_deploy_3_nic_11_5_4(
        HeatStack, symbols, CommonTemplateDir
):
    hc, stack = HeatStack(
        os.path.join(CommonTemplateDir, 'f5_ve_standalone_3_nic.yaml'),
        'func_test_standalone_3_nic',
        parameters={
            've_image': BIGIP_11_5_4_IMG,
            've_flavor': 'm1.xlarge',
            'external_network': 'external_network',
            'mgmt_network': 'mgmt_net',
            'network_1': 'data1_net',
            'network_2': 'data2_net',
            'f5_ve_os_ssh_key': 'testlab',
            'admin_password': symbols.bigip_admin_password,
            'root_password': symbols.bigip_root_password,
            'license': symbols.license
        }
    )
    updated_stack = hc.stacks.get(stack.id)
    floating_ip = get_floating_ip_output(updated_stack)
    bigip = wait_for_active_licensed_bigip(
        floating_ip, 'admin', symbols.bigip_admin_password,
        BIGIP_11_5_4_VERSION, 3
    )
    check_net_components(bigip, 3)


def test_f5_base_instance_deploy_3_nic_11_6(
        HeatStack, symbols, CommonTemplateDir
):
    hc, stack = HeatStack(
        os.path.join(CommonTemplateDir, 'f5_ve_standalone_3_nic.yaml'),
        'func_test_standalone_3_nic',
        parameters={
            've_image': BIGIP_11_6_IMG,
            'external_network': 'external_network',
            'mgmt_network': 'mgmt_net',
            'network_1': 'data1_net',
            'network_2': 'data2_net',
            'f5_ve_os_ssh_key': 'testlab',
            'admin_password': symbols.bigip_admin_password,
            'root_password': symbols.bigip_root_password,
            'license': symbols.license
        }
    )
    updated_stack = hc.stacks.get(stack.id)
    floating_ip = get_floating_ip_output(updated_stack)
    bigip = wait_for_active_licensed_bigip(
        floating_ip, 'admin', symbols.bigip_admin_password,
        BIGIP_11_6_VERSION, 3
    )
    check_net_components(bigip, 3)


def test_f5_base_instance_deploy_3_nic_12_0(
        HeatStack, symbols, CommonTemplateDir
):
    hc, stack = HeatStack(
        os.path.join(CommonTemplateDir, 'f5_ve_standalone_3_nic.yaml'),
        'func_test_standalone_3_nic',
        parameters={
            've_image': BIGIP_12_0_IMG,
            'external_network': 'external_network',
            'mgmt_network': 'mgmt_net',
            'network_1': 'data1_net',
            'network_2': 'data2_net',
            'f5_ve_os_ssh_key': 'testlab',
            'admin_password': symbols.bigip_admin_password,
            'root_password': symbols.bigip_root_password,
            'license': symbols.license
        }
    )
    updated_stack = hc.stacks.get(stack.id)
    floating_ip = get_floating_ip_output(updated_stack)
    bigip = wait_for_active_licensed_bigip(
        floating_ip, 'admin', symbols.bigip_admin_password,
        BIGIP_12_0_VERSION, 3
    )
    check_net_components(bigip, 3)
