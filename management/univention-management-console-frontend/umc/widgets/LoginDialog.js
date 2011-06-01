/*global dojo dijit dojox umc console window */

dojo.provide("umc.widgets.LoginDialog");

dojo.require("dijit.form.Button");
dojo.require("dijit.form.TextBox");
dojo.require("dijit.layout.ContentPane");
dojo.require("dojox.layout.TableContainer");
dojo.require("dojox.widget.Dialog");
dojo.require("umc.tools");
dojo.require("umc.widgets.StandbyMixin");
dojo.require("umc.widgets.ContainerForm");
dojo.require("umc.widgets.ContainerWidget");
dojo.require("umc.widgets.Form");
dojo.require("umc.widgets.Label");
dojo.require("umc.i18n");

dojo.declare('umc.widgets.LoginDialog', [ dojox.widget.Dialog, umc.widgets.StandbyMixin, umc.i18n.Mixin ], {
	// our own variables
	_layoutContainer: null,
	_passwordTextBox: null,
	_usernameTextBox: null,
	_form: null,

	// use the framework wide translation file
	i18nClass: 'umc.app',

	postMixInProperties: function() {
		dojo.mixin(this, {
			closable: false,
			modal: true,
			sizeDuration: 900,
			sizeMethod: 'chain',
			sizeToViewport: false,
			dimensions: [300, 250]
		});

	},

	buildRendering: function() {
		this.inherited(arguments);

		var widgets = [{
			type: 'TextBox',
			name: 'username',
			value: dojo.cookie('UMCUsername') || '',
			description: this._('The username of your domain account.'),
			label: this._('Username')
		}, {
			type: 'PasswordBox',
			name: 'password',
			description: this._('The password of your domain account.'),
			label: this._('Password')
		}, {
			type: 'ComboBox',
			name: 'language',
			staticValues: {
				de: this._('German'),
				en: this._('English')
			},
			value: dojo.locale.substring(0, 2),
			description: this._('The language for the login session.'),
			label: this._('Language')
		}];

		var buttons = [{
			name: 'submit',
			label: this._('Login'),
			callback: dojo.hitch(this, function(values) {
				// call LoginDialog.onSubmit() and clear password
				this._authenticate(values.username, values.password);
				this._form.elementValue('password', '');
			})
		}, {
			name: 'cancel',
			label: this._('Reset')
		}];

		var layout = [['username'], ['password'], ['language']];
		 
		this._form = new umc.widgets.Form({
			//style: 'width: 100%',
			widgets: widgets,
			buttons: buttons,
			layout: layout,
			cols: 1,
			orientation: 'horiz',
			region: 'center'
		}).placeAt(this.containerNode);
		this._form.startup();

		// register onChange event
		dojo.connect(this._form._widgets.language, 'onChange', this, function() {
			// reload the page when a different language is selected
			var query = dojo.queryToObject(window.location.search.substring(1));
			query.lang = this._form.elementValue('language');
			dojo.cookie('UMCLang', query.lang, { expires: 100, path: '/' });
			window.location.search = '?' + dojo.objectToQuery(query);
		});

		// put the layout together
		this._layoutContainer = new dojox.layout.TableContainer({
			cols: 1,
			showLabels: false
		});
		this._layoutContainer.addChild(new umc.widgets.Label({
			content: '<p>' + this._('Welcome to the Univention Management Console. Please enter your domain username and password for login!') + '</p>'
		}));
		this._layoutContainer.addChild(this._form);
		this.set('content', this._layoutContainer);
	},

	postCreate: function() {
		// call superclass' postCreate()
		this.inherited(arguments);

		// hide the close button
		dojo.style(this.closeButtonNode, 'display', 'none');
	},

	reset: function() {
		// description:
		//		Reset all form entries to their initial values.
		this._passwordTextBox.reset();
		this._usernameTextBox.reset();
	},

	_onKey:  function(evt) {
		// ignore ESC key
		if (evt.charOrCode == dojo.keys.ESCAPE) {
			return;
		}

		// otherwise call the standard handler
		this.inherited(arguments);
	},

	_authenticate: function(username, password) {
		this.standby(true);
		umc.tools.umcpCommand('auth', {
			username: username,
			password: password
		}).then(dojo.hitch(this, function(data) {
			// disable standby in any case
			//console.log('# _authenticate - ok');
			//console.log(data);
			this.standby(false);

			// make sure that we got data
			this.onLogin(username);
		}), dojo.hitch(this, function(error) {
			// disable standby in any case
			//console.log('# _authenticate - error');
			//console.log(error);
			this.standby(false);
		}));
	},

	onLogin: function(/*String*/ username) {
		// event stub
	}
});


