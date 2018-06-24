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
      /**
       * Convert data to format dd-mm-yyyy, if date paremeter does not
       * given, return current date
       * @return string:
       */
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

    self.isDate = function (date) {
      /**
       * Checks that date is in right format
       * @return boolean:
       */
      var dateArr = date.match(/\d{4}-\d{2}-\d{2}/);
      return Boolean(dateArr) && dateArr.length > 0;
    };

    self.initRequest = function () {
      /** define client priority value */
      self.newRequest({
        title: null,
        description: null,
        client: self.chosenClient(),
        target_date: self.getDate(),
        product_area: null
      });
      location.hash = '#profile/requests';
    };

    self.err = function (msg) {
      /** default error message */
      if (msg.status && msg.responseText.length < 100) {
        self.message({error: msg.responseText});
      }
      else {
        $('#body').html(msg.responseText);
      }
        // self.message({error: 'Server is not available'});
    };

    self.closeModals = function () {
      /** close a modal window */
      $('#modalLogin').modal('hide');
      $('#modalRegister').modal('hide');
    };

    // TODO: return the user credentials
    self.getCredentials = function () {
      /**
       * Return a string credentials encoded in Base64
       *  - credentials is or a token from a back-end server or
       *    user and password
       *
       * @return: string
       */
      if (self.token()) return "Basic " + btoa(self.token() + ":");
      else if (self.credentials().email && self.credentials().password) {
        var credentials = self.credentials();
        return "Basic " + btoa(credentials.email + ":" + credentials.password);
      } else return "";
    };

    self.updateToken = function () {
      /** Get a token from back-end and save it */
      self.location.post('/token', null, function (res) {
        if (res.user !== undefined && res.token !== undefined) {
          self.user(res.user);
          self.token(res.token);
        } else {
          self.message({error: 'Server is not available.'})
        }
      }, self.err);
    };

    // TODO: location and requests
    self.location = {
      uri: function (url) {
        /** add csrf token as a GET parameter to url */
        return self.host + url + '?csrf=' + self.getCSRFToken();
      },
      get: function (url, callback, err) {
        /** prepare and execute a GET request */
        var data = {
          type: 'GET',
          url: self.location.uri(url),
          processData: false,
          dataType: 'JSON',
          headers: {"Authorization": self.getCredentials()},
          contentType: 'application/json; charset=utf-8',
          statusCode: {401: self.updateToken},
          success: callback,
          error: err
        };
        $.ajax(data);
      },
      post: function (url, data, callback, err) {
        /** prepare and execute a POST request */
        $.ajax({
          type: 'POST',
          url: self.location.uri(url),
          processData: false,
          dataType: 'JSON',
          data: ko.toJSON(data),
          headers: {"Authorization": self.getCredentials()},
          contentType: 'application/json; charset=utf-8',
          statusCode: {401: self.updateToken},
          success: callback,
          error: err
        });
      }
    };

    self.getCSRFToken = function () {
      /**
       * Get csrf token string from the page
       * @return: string
       */
      return $('#csrf-token').data('csrf-token');
    };

    self.GoogleLogin = function () {
      /**
       * Provide a google authorization and send google token to back-end
       * @type {HTMLElement | null}
       */
      var googleMeta = document.getElementById('google-app-id');
      var googleCallBack = function (result) {
        /** Callback function for Google OAuth */
        if (result['code']) {
          function successLogin(res) {
            /** Callback for success response from back-end  */
            if (res) {
              self.user(res.user);
              self.token(res.token);
              self.closeModals();
              location.hash = '#profile';
            } else if (res.error) {
              self.message({error: res.error});
              console.log(res.error);
            }
          }

          self.location.post('/oauth/google', {code: result['code']},
            successLogin, self.err)
        }
      };
      // get Google OAuth configuration
      self.googleParams = {
        'clientid': googleMeta.getAttribute('data-clientid'),
        'cookiepolicy': googleMeta.getAttribute('data-cookiepolicy'),
        'redirecturi': googleMeta.getAttribute('data-redirecturi'),
        'accesstype': googleMeta.getAttribute('data-accesstype'),
        'approvalprompt': googleMeta.getAttribute('data-approvalprompt'),
        'scope': googleMeta.getAttribute('data-scope'),
        'callback': googleCallBack
      };
      gapi.auth.signIn(self.googleParams);
    };

    self.userValid = function () {
      /** check user is not empty */
      return self.user().email && self.user().first_name && self.user().last_name
    };

    self.passwordsValid = function () {
      /** check the passwords are equal */
      return self.passwords().p1 && self.passwords().p2 && self.passwords().p1 === self.passwords().p2;
    };

    self.onLogin = function () {

      self.closeModals();
      if (self.credentials().email && self.credentials().password) {

        function successLogin(res) {
          if (res.user !== undefined && res.token !== undefined) {
            self.user(res.user);
            self.token(res.token);
            location.hash = '#profile';
          } else {
            self.message({error: 'Server is not available.'})
          }
        }

        self.location.post('/token', null, successLogin, self.err);
      } else {
        self.message({error: 'Email or password can\'t to be empty'});
      }
    };

  };

  ko.applyBindings(new ViewModel());
}());
