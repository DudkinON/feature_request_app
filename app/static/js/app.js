(function () {

  // TODO: upload Google client
  (function (d, s, id) {
    /**
     * Upload Google OAuth API library, and run callback when
     * the library is loaded.
     */
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
      return;
    }
    js = d.createElement(s);
    js.id = id;
    js.src = "https://apis.google.com/js/client.js?onload=onLoadedGoogle";
    js.async = true;
    fjs.parentNode.insertBefore(js, fjs);
  }(document, 'script', 'google-sign-in-script'));

  // TODO: function onLoadFunction
  function onLoadedGoogle() {
    /**
     * Function which run after Google OAuth API
     * library will loaded.
     */
    gapi.client.setApiKey(
      document.getElementById('google-app-id').getAttribute('data-key-api'));
    gapi.client.load('plus', 'v1', function () {
    });
  }

  var Worker = function () {
    /** Object which managements data and contained logical of SPA */
    var self = this;

    // Define scope
    self.host = ""; // change for use cross site request
    self.menu = ['about', 'license'];
    self.requestMenu = ['user', 'requests'];
    self.login = ko.observable(false);
    self.user = ko.observable();
    self.message = ko.observable();
    self.data = ko.observable();
    self.token = ko.observable(null);
    self.passwords = ko.observable({p1: null, p2: null});
    self.credentials = ko.observable({email: null, password: null});
    self.clients = ko.observableArray();
    self.newClient = ko.observable('');
    self.editClient = ko.observable('');
    self.chosenClient = ko.observable();
    self.areas = ko.observableArray();
    self.newProductArea = ko.observable('');
    self.editProductArea = ko.observable('');
    self.requests = ko.observableArray();
    self.completedRequests = ko.observableArray();
    self.requestInfo = ko.observable();
    self.newRequest = ko.observable();
    self.editRequest = ko.observable();
    self.markRequest = ko.observable();
    self.removeRequest = ko.observable();
    self.selectedClient = ko.observable();
    self.selectedProductArea = ko.observable();

    self.getDate = function (date) {

      var _date;

      if (date === undefined) _date = new Date();
      else _date = new Date(date);

      var day = _date.getDate();
      var month = _date.getMonth() + 1;
      var year = _date.getFullYear();

      if (day < 10) day = '0' + day;
      if (month < 10) month = '0' + month;

      _date = year + '-' + month + '-' + day;
      $('#target_date').data(_date);
      return _date;
    };

  };

}());
