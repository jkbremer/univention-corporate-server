/*global console MyError dojo dojox dijit umc */

dojo.provide("umc.modules.groupadmin");

dojo.require("umc.widgets.TabbedModule");
dojo.require("umc.widgets.Module");
dojo.require( "umc.widgets.Form" );
dojo.require( "umc.widgets.Grid" );
dojo.require( "dojox.layout.TableContainer" );
dojo.require( "dijit.layout.BorderContainer" );

dojo.declare("umc.modules.groupadmin", umc.widgets.TabbedModule, {
	// summary:
	//		Module for modifying and displaying UCR variables on the system.

	_grid: null,
	_store: null,
	_searchWidget: null,
	_detailDialog: null,
	_contextVariable: null,

	buildRendering: function() {
		// call superclass' method
		this.inherited(arguments);
		this.addTab( 'Übersicht', this.overviewTab() );
		this.addTab( 'Lehrerzuordnung', '&lt;Leer&gt;' );
		this.addTab( 'Ungenutzte Gruppen', '&lt;Leer&gt;' );
	},

	overviewTab: function() {
		var tmpCallback = dojo.hitch(this, function(selection) {
			// logout users after confirmation
			umc.app.confirm('Sind Sie sicher, dass Sie diese Testaktion ausführen wollen?', [{
				label: 'Ausführen',
				'default': true,
				callback: function() {
					umc.app.notify('Die Testaktion wurde ausgeführt?');
				}
			}, {
				label: 'Abbrechen'
			}]);
		});

		// define actions
		var actions = [{
			name: 'add',
			label: 'Hinzufügen',
			description: 'Hinzufügen einer neuen Gruppe.',
			iconClass: 'dijitIconNewTask',
			isContextAction: false,
			isStandardAction: true,
			isMultiAction: false
		}, {
			name: 'edit',
			label: 'Bearbeiten',
			description: 'Bearbeiten der ausgewählten Gruppen.',
			iconClass: 'dijitIconEdit',
			isStandardAction: true,
			isContextAction: true,
			callback: dojo.hitch( this, function( vars ) {
				console.log( vars );
				this._searchWidget.umcpGet( { 'group' : vars } );
			})
		}, {
			name: 'delete',
			label: 'Löschen',
			description: 'Löschen der ausgewählten UCR-Variablen.',
			iconClass: 'dijitIconDelete',
			isStandardAction: true,
			isContextAction: true,
			callback: dojo.hitch(this, function(selection) {
				// get all users
				var groups = [];
				dojo.forEach(selection, function(i) {
					groups.push(i.name);
				});
				var groupsStr = groups.join(', ');

				// logout users after confirmation
				umc.app.confirm('Sind Sie sicher, dass Sie die folgenden Gruppen löschen möchten: ' + groupsStr + ' ?', [{
					label: 'Löschen',
					'default': true,
					callback: function() {
						umc.app.notify('Die folgenden Gruppen wurden gelöscht: ' + groupsStr);
					}
				}, {
					label: 'Abbrechen'
				}]);
			})
		}, {
			name: 'test1',
			label: 'Zusatzaktion',
			description: 'Dies ist nur eine Testaktion.',
			isStandardAction: false,
			isContextAction: true,
			callback: tmpCallback
		}, {
			name: 'test2',
			label: 'Noch eine Zusatzaktion',
			description: 'Dies ist nur eine Testaktion.',
			isStandardAction: false,
			isContextAction: true,
			callback: tmpCallback
		}, {
			name: 'test3',
			label: 'Dritte Zusatzaktion',
			description: 'Dies ist nur eine Testaktion.',
			isStandardAction: false,
			isContextAction: true,
			callback: tmpCallback
		}];

		// define grid columns
		var columns = [{
			name: 'name',
			label: 'Gruppe',
			description: 'Name der Gruppe',
			editable: false
		}, {
			name: 'description',
			label: 'Beschreibung',
			description: 'Eine kurze Beschreibung zu der Gruppe',
			editable: false
		}];

		// generate the data grid
		this._grid = new umc.widgets.Grid({
			region: 'center',
			actions: actions,
			columns: columns,
			idField: 'name',
			umcpSearchCommand: 'groupadmin/search'
		});

		//
		// add search widget
		//

		// define the different search widgets
		var widgets = [{
			type: 'TextBox',
			name: 'name',
			value: '*',
			description: 'Ein Begriff, der im Gruppennamen gesucht wird',
			label: 'Name'
		}, {
			type: 'TextBox',
			name: 'description',
			value: '*',
			description: 'Ein Begriff, der in der Gruppenbeschreibung gesucht wird',
			label: 'Beschreibung'
		}];

		// define all buttons
		var buttons = [{
			name: 'submit',
			label: 'Suchen',
			callback: dojo.hitch(this._grid, 'umcpSearch')
		}, {
			name: 'reset',
			label: 'Zurücksetzen'
		}];

		// define the search form layout
		var layout = [
			[ 'name', 'description' ]
		];

		// generate the search widget
		this._searchWidget = new umc.widgets.Form({
			region: 'top',
			widgets: widgets,
			buttons: buttons,
			layout: layout,
			umcpSetCommand: 'groupadmin/set',
			umcpGetCommand: 'groupadmin/get'
		});
		
		// simple handler to enable/disable standby mode
		dojo.connect(this._grid, 'umcpSearch', this, function() {
			this.standby(true);
		});
		dojo.connect(this._grid, 'onUmcpSearchDone', this, function() {
			this.standby(false);
		});

		// put everything together
		var module = new umc.widgets.Module({
			description: 'Hier können Gruppen für Arbeitskreise oder Projekte angelegt, bearbeitet oder gelöscht werden. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus vehicula purus eu ipsum tempus quis vestibulum nunc aliquet. Donec sapien nunc, tempor sit amet malesuada vitae, cursus quis urna. Aenean molestie tempus faucibus. Donec at varius nisl. Pellentesque lobortis suscipit ante at dictum. Nulla sed mauris eget dolor pellentesque egestas at a nisl. Nam mollis urna in ipsum placerat vitae sagittis purus tristique.'
		});
		module.addChild( this._searchWidget );
		module.addChild( this._grid ) ;
		//		return [ this._searchWidget, this._grid ];
		return module;
	}

});


