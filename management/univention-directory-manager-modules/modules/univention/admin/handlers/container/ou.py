# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  admin module for the organizational unit objects
#
# Copyright 2004-2019 Univention GmbH
#
# http://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <http://www.gnu.org/licenses/>.

from univention.admin.layout import Tab, Group
from univention.admin import configRegistry
import univention.admin.uldap
import univention.admin.syntax
import univention.admin.filter
import univention.admin.handlers
import univention.admin.localization
import univention.debug
import ldap

translation = univention.admin.localization.translation('univention.admin.handlers.container')
_ = translation.translate

module = 'container/ou'
operations = ['add', 'edit', 'remove', 'search', 'move', 'subtree_move']
childs = 1
short_description = _('Container: Organisational Unit')
object_name = _('Organisational Unit')
object_name_plural = _('Organisational Units')
long_description = ''
options = {
	'default': univention.admin.option(
		default=True,
		objectClasses=['top', 'organizationalUnit']
	),
}
property_descriptions = {
	'name': univention.admin.property(
		short_description=_('Name'),
		long_description='',
		syntax=univention.admin.syntax.string,
		multivalue=False,
		include_in_default_search=True,
		options=[],
		required=True,
		may_change=True,
		identifies=True,
		readonly_when_synced=True,
	),
	'policyPath': univention.admin.property(
		short_description=_('Add to standard policy containers'),
		long_description='',
		syntax=univention.admin.syntax.boolean,
		multivalue=False,
		options=[],
		required=False,
		may_change=True,
		identifies=False,
	),
	'dhcpPath': univention.admin.property(
		short_description=_('Add to standard DHCP containers'),
		long_description='',
		syntax=univention.admin.syntax.boolean,
		multivalue=False,
		options=[],
		required=False,
		may_change=True,
		identifies=False,
	),
	'dnsPath': univention.admin.property(
		short_description=_('Add to standard DNS containers'),
		long_description='',
		syntax=univention.admin.syntax.boolean,
		multivalue=False,
		options=[],
		required=False,
		may_change=True,
		identifies=False,
	),
	'userPath': univention.admin.property(
		short_description=_('Add to standard user containers'),
		long_description='',
		syntax=univention.admin.syntax.boolean,
		multivalue=False,
		options=[],
		required=False,
		may_change=True,
		identifies=False,
	),
	'groupPath': univention.admin.property(
		short_description=_('Add to standard group containers'),
		long_description='',
		syntax=univention.admin.syntax.boolean,
		multivalue=False,
		options=[],
		required=False,
		may_change=True,
		identifies=False,
	),
	'computerPath': univention.admin.property(
		short_description=_('Add to standard computer containers'),
		long_description='',
		syntax=univention.admin.syntax.boolean,
		multivalue=False,
		options=[],
		required=False,
		may_change=True,
		identifies=False,
	),
	'networkPath': univention.admin.property(
		short_description=_('Add to standard network containers'),
		long_description='',
		syntax=univention.admin.syntax.boolean,
		multivalue=False,
		options=[],
		required=False,
		may_change=True,
		identifies=False,
	),
	'sharePath': univention.admin.property(
		short_description=_('Add to standard share containers'),
		long_description='',
		syntax=univention.admin.syntax.boolean,
		multivalue=False,
		options=[],
		required=False,
		may_change=True,
		identifies=False,
	),
	'printerPath': univention.admin.property(
		short_description=_('Add to standard printer containers'),
		long_description='',
		syntax=univention.admin.syntax.boolean,
		multivalue=False,
		options=[],
		required=False,
		may_change=True,
		identifies=False,
	),
	'mailPath': univention.admin.property(
		short_description=_('Add to standard mail containers'),
		long_description='',
		syntax=univention.admin.syntax.boolean,
		multivalue=False,
		options=[],
		required=False,
		may_change=True,
		identifies=False,
	),
	'licensePath': univention.admin.property(
		short_description=_('Add to standard license containers'),
		long_description='',
		syntax=univention.admin.syntax.boolean,
		multivalue=False,
		options=[],
		required=False,
		may_change=True,
		identifies=False,
	),
	'description': univention.admin.property(
		short_description=_('Description'),
		long_description='',
		syntax=univention.admin.syntax.string,
		multivalue=False,
		include_in_default_search=True,
		options=[],
		required=False,
		may_change=True,
		identifies=False,
		readonly_when_synced=True,
	),
}

layout = [
	Tab(_('General'), _('Basic settings'), layout=[
		Group(_('Organisational unit description'), layout=[
			["name", "description"],
		]),
		Group(_('Container settings'), _('Default position when adding objects'), layout=[
			["userPath", "groupPath"],
			["computerPath", "policyPath"],
			["dnsPath", "dhcpPath"],
			["networkPath", "sharePath"],
			["printerPath", "mailPath"],
			"licensePath",
		]),
	]),
]

mapping = univention.admin.mapping.mapping()
mapping.register('name', 'ou', None, univention.admin.mapping.ListToString)
mapping.register('description', 'description', None, univention.admin.mapping.ListToString)


class object(univention.admin.handlers.simpleLdap):
	module = module

	PATH_KEYS = {
		'userPath': 'univentionUsersObject',
		'groupPath': 'univentionGroupsObject',
		'computerPath': 'univentionComputersObject',
		'policyPath': 'univentionPolicyObject',
		'dnsPath': 'univentionDnsObject',
		'dhcpPath': 'univentionDhcpObject',
		'networkPath': 'univentionNetworksObject',
		'sharePath': 'univentionSharesObject',
		'printerPath': 'univentionPrintersObject',
		'mailPath': 'univentionMailObject',
		'licensePath': 'univentionLicenseObject',
	}

	def open(self):
		univention.admin.handlers.simpleLdap.open(self)

		pathResult = self.lo.get('cn=directory,cn=univention,' + self.position.getDomain())
		self.default_dn = 'cn=directory,cn=univention,' + self.position.getDomain()
		if not pathResult:
			pathResult = self.lo.get('cn=default containers,cn=univention,' + self.position.getDomain())
			self.default_dn = 'cn=default containers,cn=univention,' + self.position.getDomain()

		for prop in self.PATH_KEYS:
			self[prop] = '0'

		for prop, attr in self.PATH_KEYS.iteritems():
			if any(x == self.dn for x in pathResult.get(attr, [])):
				self[prop] = '1'

		self.save()

	def _ldap_pre_create(self):
		super(object, self)._ldap_pre_create()
		if configRegistry.is_false('directory/manager/child/cn/ou', True):
			if self.position.getDn() != configRegistry.get('ldap/base'):
				# it is possible to have a basedn with cn=foo
				# in this case it is allowed to create a ou
				# under a cn.
				m = univention.admin.modules.identifyOne(self.position.getDn(), self.lo.get(self.position.getDn()))
				if m.module == 'container/cn':
					raise univention.admin.uexceptions.invalidChild(_('It is not allowed to create a container/ou as child object of a container/cn.'))

	def _ldap_post_create(self):
		changes = []

		for (prop, attr) in self.PATH_KEYS.items():
			if self.oldinfo.get(prop) != self.info.get(prop):
				entries = self.lo.getAttr(self.default_dn, attr)
				if self.info[prop] == '0':
					if self.dn in entries:
						changes.append((attr, self.dn, ''))
				else:
					if self.dn not in entries:
						changes.append((attr, '', self.dn))

		if changes:
			self.lo.modify(self.default_dn, changes)

	def _ldap_pre_modify(self):
		if self.hasChanged('name'):
			newdn = 'ou=%s,%s' % (ldap.dn.escape_dn_chars(self.info['name']), self.lo.parentDn(self.dn))
			self.move(newdn)

	def _ldap_post_move(self, olddn):
		settings_module = univention.admin.modules.get('settings/directory')
		settings_object = univention.admin.objects.get(settings_module, None, self.lo, position='', dn=self.default_dn)
		settings_object.open()
		for attr in ['dns', 'license', 'computers', 'shares', 'groups', 'printers', 'policies', 'dhcp', 'networks', 'users', 'mail']:
			if olddn in settings_object[attr]:
				settings_object[attr].remove(olddn)
				settings_object[attr].append(self.dn)
		settings_object.modify()

	def _ldap_post_modify(self):
		changes = []

		for prop, attr in self.PATH_KEYS.items():
			if self.oldinfo.get(prop) != self.info.get(prop):
				if self.info[prop] == '0':
					changes.append((attr, self.dn, ''))
				else:
					changes.append((attr, '', self.dn))
		if changes:
			self.lo.modify(self.default_dn, changes)

	def _ldap_pre_remove(self):
		changes = []

		self.open()

		for prop, attr in self.PATH_KEYS.items():
			if self.oldinfo.get(prop) == '1':
				changes.append((attr, self.dn, ''))
		self.lo.modify(self.default_dn, changes)

	@classmethod
	def unmapped_lookup_filter(cls):
		return univention.admin.filter.conjunction('&', [
			univention.admin.filter.expression('objectClass', 'organizationalUnit'),
			univention.admin.filter.conjunction('!', [univention.admin.filter.expression('objectClass', 'univentionBase')])
		])


lookup = object.lookup


def identify(dn, attr, canonical=0):
	return 'organizationalUnit' in attr.get('objectClass', []) and 'univentionBase' not in attr.get('objectClass', [])
