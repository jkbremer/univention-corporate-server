# -*- coding: utf-8 -*-
# pylint: disable-msg=C0301
#
# Copyright (C) 2008-2020 Univention GmbH
#
# https://www.univention.de/
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
# <https://www.gnu.org/licenses/>.

import univention.ucslint.base as uub
import re
import os

CALLED, COPIED = (1 << bit for bit in range(2))


class UniventionPackageCheck(uub.UniventionPackageCheckDebian):

	def getMsgIds(self):
		return {
			'0001-1': (uub.RESULT_STYLE, 'the old command "univention-admin" is used'),
			'0001-2': (uub.RESULT_ERROR, '"$@" for passing credentials to univention-directory-manager is missing'),
			'0001-3': (uub.RESULT_WARN, 'join scripts are now versioned - the variable VERSION is not set'),
			'0001-4': (uub.RESULT_WARN, 'join scripts are now versioned - the string " v${VERSION} " within grep/echo is missing'),
			'0001-5': (uub.RESULT_ERROR, 'debian/rules is missing'),
			'0001-6': (uub.RESULT_WARN, 'join script seems not to be installed via debian/rules'),
			'0001-7': (uub.RESULT_WARN, 'join script seems not to be called in any postinst file'),
			'0001-8': (uub.RESULT_WARN, 'join scripts should be called with "|| true" do avoid failing postinst scripts if "set -e" is used'),
			'0001-9': (uub.RESULT_WARN, 'cannot open specified file'),
			'0001-10': (uub.RESULT_ERROR, 'join script contains "eval $(ucr shell)" without proper quoting'),  # unused, moved to 0017
			'0001-11': (uub.RESULT_ERROR, 'join script contains lines with unquoted $@'),
			'0001-12': (uub.RESULT_ERROR, 'join script contains more than one line with VERSION=  statement'),
			'0001-13': (uub.RESULT_ERROR, 'join script does not include "joinscripthelper.lib"'),
			'0001-14': (uub.RESULT_ERROR, 'join script does not call "joinscript_init"'),
			'0001-15': (uub.RESULT_ERROR, 'join script does not call "joinscript_save_current_version"'),
			'0001-16': (uub.RESULT_ERROR, 'join script does not use joinscript api (possible clear text passwords)'),
			'0001-17': (uub.RESULT_WARN, 'unjoin script seems not to be called in any postrm file'),
			'0001-18': (uub.RESULT_WARN, 'unjoin script seems not to be copied in any prerm file'),
			'0001-19': (uub.RESULT_ERROR, 'unjoin script must not call "joinscript_save_current_version"'),
			'0001-20': (uub.RESULT_ERROR, 'unjoin script does not call "joinscript_remove_script_from_status_file"'),
			'0001-21': (uub.RESULT_WARN, 'unjoin script does not call "joinscript_init"'),
		}

	RE_LINE_ENDS_WITH_TRUE = re.compile(r'\|\|[ \t]+true[ \t]*$')
	RE_LINE_CONTAINS_SET_E = re.compile(r'\n[\t ]*set -e', re.M)
	RE_DH_UMC = re.compile(r'\bdh-umc-module-install\b')
	RE_DH_JOIN = re.compile(r'\bunivention-install-joinscript\b')

	def check_join_script(self, filename):
		"""Check a single join script."""
		try:
			content = open(filename, 'r').read()
		except EnvironmentError:
			self.addmsg('0001-9', 'failed to open and read file', filename)
			return

		self.debug('checking %s' % filename)

		is_uninstall = filename.endswith('.uinst')
		lines = content.splitlines()
		cnt = {
			'version': 0,
			'vversion': 0,
			'joinscripthelper.lib': 0,
			'joinscript_init': 0,
			'joinscript_save_current_version': 0,
			'joinscript_api': False,
			'joinscript_remove_script_from_status_file': 0,
		}
		for lnr, line in enumerate(lines, start=1):
			line = line.strip()

			# check joinscript api
			if line.startswith('## joinscript api:'):
				cnt['joinscript_api'] = True

			if not line or line.startswith('#'):
				continue

			# check for old style joinscript
			if line.startswith('VERSION='):
				cnt['version'] += 1
				if cnt['version'] > 1:
					self.addmsg('0001-12', 'join script does set VERSION more than once', filename, lnr)
			if line.find(' v${VERSION} ') >= 0:
				cnt['vversion'] += 1

			# check for new style joinscript
			if line.startswith('source /usr/share/univention-join/joinscripthelper.lib') or line.startswith('. /usr/share/univention-join/joinscripthelper.lib'):
				cnt['joinscripthelper.lib'] += 1
			if 'joinscript_init' in line:
				cnt['joinscript_init'] += 1
			if 'joinscript_save_current_version' in line:
				cnt['joinscript_save_current_version'] += 1
			if 'joinscript_remove_script_from_status_file' in line:
				cnt['joinscript_remove_script_from_status_file'] += 1

			# check udm calls
			if 'univention-admin ' in line or 'univention-directory-manager ' in line or 'udm ' in line:
				if 'univention-admin ' in line:
					self.addmsg('0001-1', 'join script still uses "univention-admin"', filename, lnr)

				if ' $@ ' not in line and ' "$@" ' not in line and ' "${@}" ' not in line:
					self.addmsg('0001-2', 'join script is missing "$@"', filename, lnr)

			if ' $@ ' in line or ' ${@} ' in line:
				self.addmsg('0001-11', 'join script contains unquoted $@', filename, lnr)

		if not cnt['joinscript_api']:
			self.addmsg('0001-16', 'join script does not use joinscript api (possible clear text passwords)', filename)

		if cnt['version'] == 0:
			self.addmsg('0001-3', 'join script does not set VERSION', filename)

		if not cnt['joinscripthelper.lib']:
			# no usage of joinscripthelper.lib
			if cnt['vversion'] > 0 and cnt['vversion'] < 2:
				self.addmsg('0001-4', 'join script does not grep for " v${VERSION} "', filename)
			elif cnt['vversion'] == 0:
				self.addmsg('0001-13', 'join script does not use joinscripthelper.lib', filename)
		else:
			if is_uninstall:
				if not cnt['joinscript_init']:
					self.addmsg('0001-21', 'unjoin script does not call "joinscript_init"', filename)
				if cnt['joinscript_save_current_version']:
					self.addmsg('0001-19', 'unjoin script must not use joinscript_save_current_version', filename)
				if not cnt['joinscript_remove_script_from_status_file']:
					self.addmsg('0001-20', 'unjoin script does not call "joinscript_remove_script_from_status_file"', filename)
			else:
				if not cnt['joinscript_init']:
					self.addmsg('0001-14', 'join script does not use joinscript_init', filename)
				if not cnt['joinscript_save_current_version']:
					self.addmsg('0001-15', 'join script does not use joinscript_save_current_version', filename)

	def check(self, path):
		""" the real check """
		super(UniventionPackageCheck, self).check(path)

		fnlist_joinscripts = {}

		#
		# search join scripts
		#
		for f in os.listdir(path):
			if not f[0:2].isdigit():
				continue
			fn = os.path.join(path, f)
			if f.endswith('.inst'):
				fnlist_joinscripts[fn] = CALLED
			elif f.endswith('.uinst'):
				fnlist_joinscripts[fn] = CALLED | COPIED
			else:
				continue
			self.debug('found %s' % fn)

		#
		# check if join scripts use versioning
		#
		for js in fnlist_joinscripts:
			self.check_join_script(js)

		#
		# check if join scripts are present in debian/rules || debian/*.install
		#
		found = {}
		debianpath = os.path.join(path, 'debian')
		# get all .install files
		fnlist = list(uub.FilteredDirWalkGenerator(debianpath, suffixes=['.install']))
		# append debian/rules
		fn_rules = os.path.join(path, 'debian', 'rules')
		fnlist.append(fn_rules)

		# Look for dh-umc-modules-install
		try:
			content = open(fn_rules, 'r').read()
		except EnvironmentError:
			self.addmsg('0001-9', 'failed to open and read file', fn_rules)
		else:
			if UniventionPackageCheck.RE_DH_JOIN.search(content):
				self.debug('Detected use of univention-install-joinscript')
				try:
					fn_control = os.path.join(path, 'debian', 'control')
					parser = uub.ParserDebianControl(fn_control)
				except uub.UCSLintException:
					self.debug('Errors in debian/control. Skipping here')
				else:
					for binary_package in parser.binary_sections:
						package = binary_package.get('Package')
						for js in fnlist_joinscripts:
							if re.match(r'^\./\d\d%s\.u?inst$' % re.escape(package), js):
								self.debug('univention-install-joinscript will take care of %s' % js)
								fnlist_joinscripts[js] = 0
								found[js] = found.get(js, 0) + 1

			if UniventionPackageCheck.RE_DH_UMC.search(content):
				self.debug('Detected use of dh-umc-module-install')
				for fn in uub.FilteredDirWalkGenerator(debianpath, suffixes=['.umc-modules']):
					package = os.path.basename(fn)[:-len('.umc-modules')]
					inst = '%s.inst' % (package,)
					uinst = '%s.uinst' % (package,)
					for js in fnlist_joinscripts:
						if js.endswith(inst) or js.endswith(uinst):
							self.debug('%s installed by dh-umc-module-install' % (js,))
							found[js] = found.get(js, 0) + 1
							fnlist_joinscripts[js] = 0

		for fn in fnlist:
			try:
				content = open(fn, 'r').read()
			except EnvironmentError:
				self.addmsg('0001-9', 'failed to open and read file', fn)
				continue

			for js in fnlist_joinscripts:
				name = os.path.basename(js)
				self.debug('looking for %s in %s' % (name, fn))
				if name in content:
					self.debug('found %s in %s' % (name, fn))
					found[js] = found.get(js, 0) + 1

		for js in fnlist_joinscripts:
			if found.get(js, 0) == 0:
				self.addmsg('0001-6', 'join script is not mentioned in debian/rules or *.install files', js)

		#
		# check if join scripts are present in debian/*{pre,post}{inst,rm}
		#
		for f in os.listdir(os.path.join(path, 'debian')):
			if '.debhelper.' in f:
				continue

			if f.endswith('.postinst') or f == 'postinst':
				bit = CALLED
			elif f.endswith('.prerm') or f == 'prerm':
				bit = COPIED
			elif f.endswith('.postrm') or f == 'postrm':
				bit = CALLED
			else:
				continue

			fn = os.path.join(path, 'debian', f)
			self.debug('loading %s' % (fn))
			try:
				content = open(fn, 'r').read()
			except EnvironmentError:
				self.addmsg('0001-9', 'failed to open and read file', fn)
				continue

			set_e = UniventionPackageCheck.RE_LINE_CONTAINS_SET_E.search(content)
			if set_e:
				self.debug('found "set -e" in %s' % fn)

			for js in fnlist_joinscripts:
					name = os.path.basename(js)
					self.debug('looking for %s in %s' % (name, fn))
					if name in content:
						fnlist_joinscripts[js] &= ~bit
						self.debug('found %s in %s' % (name, fn))

						if set_e:
							for lnr, line in enumerate(content.splitlines(), start=1):
								if name in line:
									match = UniventionPackageCheck.RE_LINE_ENDS_WITH_TRUE.search(line)
									if not match:
										self.addmsg('0001-8', 'the join script %s is not called with "|| true" but "set -e" is set' % (name,), fn, lnr)

		for js, missing in fnlist_joinscripts.items():
			if missing & CALLED and js.endswith('.inst'):
				self.addmsg('0001-7', 'Join script is not mentioned in debian/*.postinst', js)
			if missing & CALLED and js.endswith('.uinst'):
				self.addmsg('0001-17', 'Unjoin script seems not to be called in any postrm file', js)
			if missing & COPIED and js.endswith('.uinst'):
				self.addmsg('0001-18', 'Unjoin script seems not to be copied in any prerm file', js)
