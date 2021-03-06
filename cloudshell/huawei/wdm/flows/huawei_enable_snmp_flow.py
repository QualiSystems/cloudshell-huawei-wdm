#!/usr/bin/python
# -*- coding: utf-8 -*-
from cloudshell.huawei.command_actions.enable_disable_snmp_actions import (
    EnableDisableSnmpActions,
)
from cloudshell.huawei.flows.huawei_enable_snmp_flow import HuaweiEnableSnmpFlow
from cloudshell.huawei.helpers.exceptions import HuaweiSNMPException
from cloudshell.snmp.snmp_parameters import SNMPWriteParameters


class HuaweiWDMEnableSnmpFlow(HuaweiEnableSnmpFlow):
    def enable_flow(self, snmp_parameters):
        if "3" not in snmp_parameters.version and not snmp_parameters.snmp_community:
            message = "SNMP community cannot be empty"
            self._logger.error(message)
            raise HuaweiSNMPException(message)

        with self._cli_handler.get_cli_service(
            self._cli_handler.config_mode
        ) as conf_session:
            snmp_actions = EnableDisableSnmpActions(conf_session, self._logger)
            if "3" in snmp_parameters.version:

                if (
                    snmp_parameters.snmp_user
                    and snmp_parameters.snmp_password
                    and snmp_parameters.snmp_private_key
                ):
                    auth_type = "privacy"
                elif snmp_parameters.snmp_user and snmp_parameters.snmp_password:
                    auth_type = "authentication"
                elif snmp_parameters.snmp_user:
                    auth_type = "noauthentication"
                else:
                    raise HuaweiSNMPException("Wrong SNMPv3 parameters")

                auth_protocol = self.ENCRYPTION.get(snmp_parameters.auth_protocol)
                if not auth_protocol:
                    raise HuaweiSNMPException(
                        "Wrong authentication protocol ({}) provided".format(
                            snmp_parameters.auth_protocol
                        )
                    )
                private_key_protocol = self.ENCRYPTION.get(
                    snmp_parameters.private_key_protocol
                )

                if not private_key_protocol:
                    raise HuaweiSNMPException(
                        "Wrong privacy key protocol ({}) provided".format(
                            snmp_parameters.private_key_protocol
                        )
                    )

                self._logger.info("Start creating SNMPv3 configuration")
                snmp_actions = EnableDisableSnmpActions(conf_session, self._logger)

                snmp_actions.enable_snmp_service()
                snmp_actions.configure_snmp_version(snmp_version="v3")
                snmp_actions.configure_snmp_v3(
                    snmp_access=self.DEFAULT_SNMP_ACCESS,
                    user=snmp_parameters.snmp_user,
                    auth_type=auth_type,
                    auth_protocol=auth_protocol,
                    auth_password=snmp_parameters.snmp_password,
                    priv_protocol=private_key_protocol,
                    priv_password=snmp_parameters.snmp_private_key,
                )
                self._logger.info(
                    "SNMP User {} created".format(snmp_parameters.snmp_user)
                )

            else:
                community = snmp_parameters.snmp_community
                if isinstance(snmp_parameters, SNMPWriteParameters):
                    raise HuaweiSNMPException(
                        "Devices doesn't support write communities"
                    )

                self._logger.info("Start creating SNMP community {}".format(community))

                snmp_actions.enable_snmp_service()
                snmp_actions.configure_snmp_version(snmp_version="v2c")
                snmp_actions.configure_snmp_community(community=community)

                self._logger.info("SNMP v2c community {} created".format(community))
