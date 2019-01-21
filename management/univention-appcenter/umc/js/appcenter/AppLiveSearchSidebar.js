/*
 * Copyright 2013-2019 Univention GmbH
 *
 * http://www.univention.de/
 *
 * All rights reserved.
 *
 * The source code of this program is made available
 * under the terms of the GNU Affero General Public License version 3
 * (GNU AGPL V3) as published by the Free Software Foundation.
 *
 * Binary versions of this program provided by Univention to you as
 * well as other copyrighted, protected or trademarked materials like
 * Logos, graphics, fonts, specific documentations and configurations,
 * cryptographic keys etc. are subject to a license agreement between
 * you and Univention and not subject to the GNU AGPL V3.
 *
 * In the case you use this program under the terms of the GNU AGPL V3,
 * the program is provided in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public
 * License with the Debian GNU/Linux or Univention distribution in file
 * /usr/share/common-licenses/AGPL-3; if not, see
 * <http://www.gnu.org/licenses/>.
 */
/*global define require console */

define([
	"dojo/_base/declare",
	"dojo/_base/lang",
	"dojo/_base/array",
	"dojo/has",
	"dojo/Deferred",
	"dojo/dom-construct",
	"dojo/regexp",
	"umc/widgets/CheckBox",
	"umc/widgets/ContainerWidget",
	"umc/widgets/Form",
	"umc/widgets/SearchBox",
	"umc/i18n!"
], function(declare, lang, array, has, Deferred, domConstruct, regexp, CheckBox, ContainerWidget, Form, SearchBox, _) {
	return declare("umc.modules.appcenter.AppLiveSearchSidebar", [ContainerWidget], {
		// summary:
		//		Offers a side bar for live searching, a set of categories can be defined.

		// categories: Object[]|String[]
		//		Array of categories exposing at least the fields 'id' and 'label'
		//		or array of strings.
		categories: null,

		// metaCategories: Object[]|String
		//		Array of labels of available meta categories.
		metaCategories: null,

		_categoriesAsIdLabelPairs: true,

		selectCategoryFormDeferred: null,

		// category: Object[]|String[]
		//		Array of the currently selected categories
		selectedCategories: [],

		selectedMetaCategories: [],

		searchLabel: null,

		selectCategoryForm: null,

		_selectCategoryForm: null,

		selectStatusForm: null,

		baseClass: 'umcLiveSearchSidebar',

		// searchableAttributes: String[]
		//		Array of strings that shall be searched.
		//		defaults to ['name', 'description', 'categories', 'keywords']
		searchableAttributes: null,

		_lastValue: '',

		buildRendering: function() {
			this.selectCategoryFormDeferred = new Deferred();
			this.inherited(arguments);
			if (this.searchableAttributes === null) {
				this.searchableAttributes = ['name', 'description', 'categories', 'keywords'];
			}

			this.searchTextBox = new ContainerWidget({ 'class': 'umcSize-FourThirds searchField'});
			this._searchTextBox = new SearchBox({
				inlineLabel: this.searchLabel || _('Search term')
			});
			this.searchTextBox.addChild(this._searchTextBox);
			this.addChild(this.searchTextBox);

		},

		postCreate: function() {
			this.inherited(arguments);

			// Reset filters, when opening the App Center:
			this.selectedCategories = [];
			this.selectedMetaCategories = [];

			this._searchTextBox.on('keyup', lang.hitch(this, function() {
				if (this.get('value') || this._lastValue) {
					// ignore empty search strings
					this._lastValue = this.get('value');
					this.onSearch();
				}
			}));
		},

		_getUniformCategory: function(category) {
			if (typeof category == 'string') {
				this._categoriesAsIdLabelPairs = false;
				return { id: category, label: category };
			}
			return category;
		},

		_isInSearchMode: function() {
			return Boolean(lang.trim(this.get('value')));
		},

		_getValueAttr: function() {
			return this._searchTextBox.get('value');
		},

		_setValueAttr: function(value) {
			return this._searchTextBox.set('value', value);
		},

		_setCategoriesAttr: function(categories) {
			if (this._selectCategoryForm) {
				this._selectCategoryForm.removeOption(this._selectCategoryForm.getOptions());
			}
			this._set('categories', categories);

			this._addCategorySelector(categories);
		},

		_addCategorySelector: function(categories) {
			var selectCategoryFormOptions = array.map(categories, lang.hitch(this, function(_category, idx) {
				var category = this._getUniformCategory(_category);
				return {
					label: category.label,
					value: category.label,
					_categoryID: category.id
				};
			}));
			
			if (this.selectCategoryForm) {
				this.removeChild(this.selectCategoryForm);
				this.selectCategoryForm.destroyRecursive();
				this.selectCategoryForm = null;
				this.selectCategoryFormDeferred = this.selectCategoryFormDeferred.isResolved() ? new Deferred() : this.selectCategoryFormDeferred;
			}
			this.selectCategoryForm = new ContainerWidget({'class': 'appLiveSearchSidebarElement'});
			domConstruct.create('span', {
				innerHTML: _('Categories'),
				'class': 'mainHeader'
			}, this.selectCategoryForm.domNode);

			var widgets = [];
			array.forEach(selectCategoryFormOptions, lang.hitch(this, function(category) {
				widgets.push({
					type: CheckBox,
					name: category.value,
					label: category.label,
					onChange: lang.hitch(this, function(arg) {
						if (arg == true) {
							this.selectedCategories.push(category.value);
						} else {
							this.selectedCategories = this.selectedCategories.filter(
								function(x) {return x != category.value;}
							);
						}
						this.onSearch();  // Trigger the refresh of the displayed Apps
					})
				});
			}));
			var form = new Form({
				widgets: widgets,
			});
			this.selectCategoryForm.addChild(form);

			this.selectCategoryFormDeferred.resolve();

			this.own(this.selectCategoryForm);
			this.addChild(this.selectCategoryForm);
		},

		_setMetaCategoriesAttr: function(metaCategories) {
			this._set('metaCategories', metaCategories);
			this._addStatusSelector(metaCategories);
		},

		_addStatusSelector: function(metaCategories) {
			if (this.selectStatusForm) {
				this.removeChild(this.selectStatusForm);
				this.selectStatusForm.destroyRecursive();
				this.selectStatusForm = null;
				this.selectStatusFormDeferred = this.selectStatusFormDeferred.isResolved() ? new Deferred() : this.selectStatusFormDeferred;
			}
			this.selectStatusForm = new ContainerWidget({'class': 'appLiveSearchSidebarElement'});
			domConstruct.create('span', {
				innerHTML: _('App status'),
				'class': 'mainHeader'
			}, this.selectStatusForm.domNode);
			this.own(this.selectStatusForm);
			this.addChild(this.selectStatusForm);

			var widgets = [];
			array.forEach(metaCategories, lang.hitch(this, function(metaCategory) {
				widgets.push({
					type: CheckBox,
					name: metaCategory,
					label: metaCategory,
					onChange: lang.hitch(this, function(arg) {
						if (arg == true) {
							this.selectedMetaCategories.push(metaCategory);
						} else {
							this.selectedMetaCategories = this.selectedMetaCategories.filter(
								function(x) {return x != metaCategory;}
							);
						}
						this.onSearch();  // Trigger the refresh of the displayed Apps
					})
				});
			}));
			var form = new Form({
				widgets: widgets,
			});
			this.selectStatusForm.addChild(form);
			this.selectStatusForm.own(form);
		},

		getSearchQuery: function(searchPattern) {
			// sanitize the search pattern
			searchPattern = regexp.escapeString(searchPattern);
			searchPattern = searchPattern.replace(/\\\*/g, '.*');
			searchPattern = searchPattern.replace(/ /g, '\\s+');

			// build together the search function
			var regex  = new RegExp(searchPattern, 'i');
			var searchableAttributes = this.searchableAttributes;
			var query = {
				test: function(value, obj) {
					var string = '';
					array.forEach(searchableAttributes, function(attr) {
						var val = obj[attr] || '';
						if (val instanceof Array) {
							val = val.join(' ');
						}
						string += val + ' ';
					});
					return regex.test(string);
				}
			};
			return query;
		},

		focus: function() {
			this._searchTextBox.focus();
		},

		onSearch: function() {
			// event stub
		},

		onCategorySelected: function() {
			//event stub
		}
	});
});

