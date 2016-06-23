# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  admin module for kerberos KDC entries
#
# Copyright 2012-2016 Univention GmbH
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
import univention.admin.filter
import univention.admin.handlers
import univention.admin.password
import univention.admin.allocators
import univention.admin.localization
import univention.admin.uldap

import ldap
import random
import string

translation=univention.admin.localization.translation('univention.admin.handlers.kerberos')
_=translation.translate

module='kerberos/kdcentry'
operations=['add','edit','remove','search','move']
childs=0
short_description=_('Kerberos: KDC Entry')
long_description=''
property_descriptions={
	'name': univention.admin.property(
			short_description=_('Principal name'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			include_in_default_search=1,
			options=[],
			required=1,
			may_change=1,
			identifies=1
		),
	'description': univention.admin.property(
			short_description=_('Description'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			include_in_default_search=1,
			required=0,
			may_change=1,
			identifies=0
		),
	'password': univention.admin.property(
			short_description=_('Password'),
			long_description='',
			syntax=univention.admin.syntax.passwd,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0,
			dontsearch=1
		),
	'generateRandomPassword': univention.admin.property(
			short_description=_('Generate random password'),
			long_description='',
			syntax=univention.admin.syntax.boolean,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0,
			dontsearch=1
		),
	'keyVersionNumber': univention.admin.property(
			short_description=_('Key version'),
			long_description='',
			syntax=univention.admin.syntax.integer,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0,
			dontsearch=1,
			default='1'
		),
	'KDCFlags': univention.admin.property(
			short_description=_('KDC Flags'),
			long_description='',
			syntax=univention.admin.syntax.integer,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0,
			dontsearch=1,
			default='126'
		),
	'maxLife': univention.admin.property(
			short_description=_('Maximum life time'),
			long_description='',
			syntax=univention.admin.syntax.integer,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0,
			dontsearch=1,
			default='86400'
		),
	'maxRenew': univention.admin.property(
			short_description=_('Maximum renew time'),
			long_description='',
			syntax=univention.admin.syntax.integer,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0,
			dontsearch=1,
			default='604800'
		),
}

layout = [
	Tab( _( 'General' ), _( 'Basic settings' ), layout = [
		Group( _( 'KDC entry' ), layout = [
			[ 'name', 'description' ],
			'password',
			'generateRandomPassword',
			'keyVersionNumber',
			'KDCFlags',
			'maxLife',
			'maxRenew',
		] ),
	] ),
 ]

mapping=univention.admin.mapping.mapping()
mapping.register('name', 'uid', None, univention.admin.mapping.ListToString)
mapping.register('description', 'description', None, univention.admin.mapping.ListToString)
mapping.register('keyVersionNumber', 'krb5KeyVersionNumber', None, univention.admin.mapping.ListToString)
mapping.register('KDCFlags', 'krb5KDCFlags', None, univention.admin.mapping.ListToString)
mapping.register('maxLife', 'krb5MaxLife', None, univention.admin.mapping.ListToString)
mapping.register('maxRenew', 'krb5MaxRenew', None, univention.admin.mapping.ListToString)

class object(univention.admin.handlers.simpleLdap):
	module=module

	def description( self ):
		# Use the name by default, otherwise the rdn will be used
		return self['name']

	def _set_principal(self):
		if self.hasChanged('name') or not hasattr(self, 'krb5PrincipalName'):
			domain=univention.admin.uldap.domain(self.lo, self.position)
			realm=domain.getKerberosRealm()
			try:
				self['name'].index('@')
			except ValueError:
				# does not contain an @
				self.krb5PrincipalName = '%s@%s' % (self['name'], realm)
			else:
				self.krb5PrincipalName = self['name']

	def _ldap_pre_create(self):
		self._set_principal()
		super(object, self)._ldap_pre_create()

	def _ldap_dn(self):
		dn = ldap.dn.str2dn(super(object, self)._ldap_dn())
		dn[0] = [('krb5PrincipalName', self.krb5PrincipalName, dn[0][0][2])]
		return ldap.dn.dn2str(dn)

	def _ldap_modlist( self ):
		ml=univention.admin.handlers.simpleLdap._ldap_modlist( self )

		self._set_principal()

		if self.hasChanged('name'):
			ml.append( ('krb5PrincipalName', self.oldattr.get('krb5PrincipalName',[]), [self.krb5PrincipalName]) )

		if self.info.get('generateRandomPassword', '').lower() in ['true', 'yes', '1']:
			self['password'] = string.join(random.sample(string.letters+string.digits, 24), '')

		if self.hasChanged('password'):
			krb_keys=univention.admin.password.krb5_asn1(self.krb5PrincipalName, self['password'])
			ml.append(('krb5Key', self.oldattr.get('krb5Key', []), krb_keys))
			
		return ml
			

	def _ldap_addlist(self):
		return [
			('objectClass', [ 'top', 'account', 'krb5Principal', 'krb5KDCEntry' ])
		]

def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', unique=0, required=0, timeout=-1, sizelimit=0):

	filter=univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression('objectClass', 'top'),
		univention.admin.filter.expression('objectClass', 'account'),
		univention.admin.filter.expression('objectClass', 'krb5Principal'),
		univention.admin.filter.expression('objectClass', 'krb5KDCEntry'),
		])

	if filter_s:
		filter_p=univention.admin.filter.parse(filter_s)
		univention.admin.filter.walk(filter_p, univention.admin.mapping.mapRewrite, arg=mapping)
		filter.expressions.append(filter_p)

	res=[]
	for dn, attrs in lo.search(unicode(filter), base, scope, [], unique, required, timeout, sizelimit):
		res.append( object( co, lo, None, dn, attributes = attrs ) )
	return res

def identify(dn, attr, canonical=0):

	ocs = attr.get('objectClass', [])

	return 'top' in ocs and 'account' in ocs and 'krb5Principal' in ocs and 'krb5KDCEntry' in ocs
