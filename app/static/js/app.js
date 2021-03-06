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
      /** user authorization with login and password */
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

    // TODO: on register
    self.onRegister = function () {
      /**
       * Close modal window and checks data if user data is
       * valid sends it to back-end
       */
      self.closeModals();
      if (!self.userValid()) {
        self.message({error: 'Fields can not to be empty', info: null});
      } else if (!self.passwordsValid()) {
        self.message({error: 'Passwords does not match'});
      } else {

        function successRegister(res) {
          /**
           * Function which will run after back-end return
           * success response. Save user data, and a token
           * from response. Redirect user to profile page.
           */
          if (res.error !== undefined) self.message({error: res.error});
          if (res.user) {
            self.user(res.user);
            self.token(res.token);
            location.hash = '#profile';
          } else {
            self.message({error: 'server is not available'});
          }
        }

        var postData = {
          email: self.user().email,
          first_name: self.user().first_name,
          last_name: self.user().last_name,
          password: self.passwords().p1
        };

        self.location.post('/registration', postData, successRegister, self.err);
      }
    };

    // TODO: update profile
    self.onUpdateProfile = function () {
      /** if equals users passwords sends updated user info to back-end */
      if (self.passwords().p1 && self.passwords().p1 === self.passwords().p2) {
        function successUpdateProfile(res) {
          if (res.error !== undefined) self.message({error: res.error});
          if (res) self.user(res);
          location.hash = '#profile'
        }

        self.location.post('/profile/update', {
          user: self.user(),
          password: self.passwords().p1
        }, successUpdateProfile, self.err);
      } else {
        self.message({error: 'Passwords do not match'})
      }

    };

    // TODO: remove profile
    self.removeProfile = function () {
      /**
       * Remove user profile
       * @param res: response from back-end
       */
      function successRemove(res) {
        self.message({info: res.info});
        self.onLogout();
        location.hash = '';
      }

      self.location.post('/profile/remove', null, successRemove, self.err);
    };

    self.onLogout = function () {
      /** Logout a user */
      self.user(null);
      self.token(null);
      self.login(false);
    };

  };

  var ViewModel = function () {
    /**
     * View model. Management display data on a page
     */
    var self = this;

    self.worker = new Worker();
    self.routeName = ko.observable(null);
    self.actionName = ko.observable(null);
    self.data = self.worker.data;

    self.checkAuth = function () {
      /** Checks that user was authorized */
      if (self.data().name === 'profile' && !self.worker.user()) {
        self.worker.onLogout();
        location.hash = '';
      } else if (self.worker.user()) self.worker.login(true);
    };

    // TODO: get requests
    self.getRequests = function () {
      /** Uploader for list of requests */
      if (!self.worker.requests() || self.worker.requests().length === 0) {
        self.worker.location.get('/requests',
          function (res) {
            self.worker.requests(res);
          }, self.err);
      }
    };

    self.getCompletedRequests = function () {
      /** Uploader for completed requests */
      if (!self.worker.completedRequests() ||
        self.worker.completedRequests().length === 0) {
        self.worker.location.get('/requests/get/completed',
          function (res) {
            self.worker.completedRequests(res);
          }, self.err);
      }
    };

    self.updateCompletedRequests = function () {
      /** Update completed requests list */
      self.worker.location.get('/requests/get/completed',
        function (res) {
          self.worker.completedRequests(res);
        }, self.err);
    };

    // TODO: get clients
    self.getClients = function () {
      /** Uploader for clients list */
      if (!self.worker.clients() || self.worker.clients().length === 0) {
        self.worker.location.get('/clients',
          function (res) {
            self.worker.clients(res);
          }, self.err);
      }
    };

    // TODO: create a new client
    self.addClient = function () {
      /** Create a new client */
      // check length of client name
      if (self.worker.newClient().length > 3) {
        // send query to back-end
        self.worker.location.post('/clients/new', {name: self.worker.newClient()},
          function (res) {
            self.worker.clients(res);
            self.worker.newClient('');
          }, self.err)
      }
      else self.worker.message({error: 'Client name too short'});
    };

    self.updateClient = function () {
      /** Update client name */
      if (self.worker.editClient().name < 3) {
        self.worker.message({error: 'Client name too short'});
      } else {
        self.worker.location.post('/clients/edit', self.worker.editClient(),
          function (res) {
            self.worker.clients(res);
          }, self.err)
      }
    };

    self.removeClient = function (client) {
      /** Remove a client */
      self.worker.location.post('/clients/delete', client,
        function (res) {
          if (res.error !== undefined) self.worker.message({error: res.error});
          else self.worker.clients(res);
        }, self.err);
    };

    // TODO: get product areas
    self.getAreas = function () {
      /** Uploader for product areas list */
      if (!self.worker.areas() || self.worker.areas().length === 0) {
        self.worker.location.get('/areas',
          function (res) {
            self.worker.areas(res);
          }, self.err);
      }
    };

    // TODO: create a new product area
    self.addProductArea = function () {
      /** Create a new product area */
      if (self.worker.newProductArea().length > 3) {
        self.worker.location.post('/areas/new', {name: self.worker.newProductArea()},
          function (res) {
            self.worker.areas(res);
            self.worker.newProductArea('');
          }, self.err)
      }
    };

    self.updateProductArea = function () {
      /** Update product area list */
      if (self.worker.editProductArea().name < 3) {
        self.worker.message({error: 'Product area too short'})
      } else {
        self.worker.location.post('/areas/edit', self.worker.editProductArea(),
          function (res) {
            if (res.error === undefined) {
              self.worker.areas(res);
            } else self.worker.message({error: res.error});
          }, self.err);
      }
    };

    self.removeProductArea = function (area) {
      /** Remove product area */
      self.worker.location.post('/areas/delete', area,
        function (res) {
          if (res.error !== undefined) self.worker.message({error: res.error});
          else self.worker.areas(res);
        }, self.err);
    };

    // TODO: route functions
    self.onProfilePath = function () {
      /** On display profile page */
      self.routeName(null);
      self.data({name: 'profile'});
      self.actionName(null);
      self.checkAuth();
      self.getRequests();
      self.getCompletedRequests();
      self.getClients();
      self.getAreas();
      self.tooltip();
    };

    self.onAboutPath = function () {
      /** On display about page */
      self.routeName(null);
      self.data({name: 'about'});
      self.actionName(null);
    };

    self.onLicensePath = function () {
      /** On display license page */
      self.routeName(null);
      self.data({name: 'license'});
      self.actionName(null);
    };

    self.onRoute = function () {
      /** On display any route */
      self.routeName(this.params.route);
      self.data({name: 'profile'});
      self.actionName(null);
      self.checkAuth();
      self.tooltip();
    };

    self.onAction = function () {
      /** On display any action */
      self.routeName(this.params.route);
      self.data({name: 'profile'});
      self.actionName(this.params.action);
      self.checkAuth();
      self.tooltip();
    };

    self.router = new Sammy(function () {
      /** Define routes and run router */
      this.get('#profile', self.onProfilePath);
      this.get('#about', self.onAboutPath);
      this.get('#license', self.onLicensePath);
      this.get('#profile/:route', self.onRoute);
      this.get('#profile/:route/:action', self.onAction);
      this.get('', function () {
        this.app.runRoute('get', '#about');
      });
    }).run();

    // TODO: close alert messages
    self.closeAlert = function () {
      self.worker.message({error: null, info: null});
    };

    // TODO: create a link for error message object
    self.err = self.worker.err;

    // TODO: open login form
    self.modalLogin = function () {
      $('#modalLogin').modal();
    };

    // TODO: open register form
    self.modalRegister = function () {
      self.worker.user({email: null, first_name: null, last_name: null});
      $('#modalRegister').modal();
    };

    // TODO: open a new client form
    self.modalNewClient = function () {
      $('#newClientModal').modal();
    };

    // TODO: open a new product area form
    self.modalNewProductArea = function () {
      $('#modalNewProductArea').modal();
    };

    self.editClient = function (elem) {
      /** Open edit client modal window */
      self.worker.editClient(elem);
      $('#editClientModal').modal();
    };

    self.editProductArea = function (area) {
      /** Open edit product area modal window */
      self.worker.editProductArea(area);
      $('#modalEditProductArea').modal();
    };

    self.markAsCompletedModal = function (request) {
      /** Open dialog for mark request as completed */
      self.worker.markRequest(request);
      $('#modalMarkAsComplete').modal();
    };

    self.removeRequestModal = function (request) {
      /** Open dialog for remove request window */
      self.worker.removeRequest(request);
      $('#modalRemoveRequest').modal();
    };

    self.removeRequest = function () {
      /** Sends POST request to back-end to remove a request */
      var data = {id: self.worker.removeRequest()['id']};
      self.worker.location.post('/requests/delete', data, function (res) {
        if (res.error === undefined) {
          self.worker.requests(res);
          self.updateCompletedRequests();
        } else self.worker.message({error: res.error});
      });
    };

    self.markRequest = function () {
      /** Sends POST request to back-end to mark a request as completed */
      var data = {id: self.worker.markRequest()['id']};
      self.worker.location.post('/requests/complete', data, function (res) {
        if (res.error === undefined) {
          self.worker.requests(res);
          self.updateCompletedRequests();
        } else self.worker.message({error: res.error});
      }, self.err)
    };

    self.goTo = function (route) {
      /** Redirect user to a route */
      location.hash = '#profile/' + route;
    };

    self.openLink = function (path) {
      /** Run tooltip and redirect user to route */
      return function () {
        self.tooltip();
        location.hash = '#profile' + path;
      };
    };

    self.goToAction = function (path) {
      /** Redirect user with given path */
      return function () {
        location.hash = '#profile/' + path;
      }
    };

    self.addRequest = function () {
      /**
       * Validate user input for a request and sends POST request to back-end
       */
      var request = self.worker.newRequest();

      if (request.title.length < 3) {
        self.worker.message({error: "Title too short"});
      }

      if (request.description.length < 10) {
        self.worker.message({error: "Description too short"});
      }

      var client = self.worker.chosenClient();

      if (client && !client.client_priority) {
        self.worker.message({error: "Client priority can't be empty"});
      }

      if (client && Number(client.client_priority) < 1) {
        self.worker.message({error: "Client priority can't be 0"});
      }

      if (!request.target_date) {
        self.worker.message({error: "Set up target date"})
      }

      if (self.worker.isDate(request.target_date)) {

        var oldDate = request.target_date;
        var dateArray = oldDate.split("-");
        var newDate = dateArray[1] + '/' + dateArray[2] + '/' + dateArray[0];

        self.worker.newRequest({
          title: request.title,
          description: request.description,
          client: self.worker.chosenClient(),
          target_date: newDate,
          product_area: request.product_area
        });
      } else self.worker.message({error: "The date has the wrong format"});

      var msg = self.worker.message();

      if (msg === undefined || msg.error === undefined) {
        self.worker.location.post('/requests/new', self.worker.newRequest(),
          function (res) {
            if (res.error) self.worker.message({error: res.error});
            else {
              self.getClients();
              self.worker.initRequest();
              self.worker.requests(res);
              self.worker.chosenClient(null);
              location.hash = '#profile/requests';
            }
          });
      }
    };

    self.openRequest = function (request) {
      /** Passes given request data to the storage and opens request page */

      // define request info
      self.worker.requestInfo(request);

      // redirect user
      location.hash = '#profile/requests/info';
    };

    self.editRequest = function (request) {
      /**
       * Prepare fields for a client and product area
       * save the data and redirect user to the request
       * edit page
       */
      var date = self.worker.getDate(request.target_date);
      self.worker.editClient(request.client);
      self.worker.selectedProductArea(request.product_area);
      self.worker.editRequest({
        id: request.id,
        title: request.title,
        description: request.description,
        client: self.worker.editClient(),
        target_date: date,
        client_priority: request.client_priority,
        product_area: request.product_area
      });
      $('#edit_client').change(function () {
        var client = self.worker.editRequest().client;
        if (client !== undefined) {
          self.worker.editClient(client);
          $('#edit_client_priority').val(client.client_priority);
        }
      });
      $('#edit_product_area').change(function () {
        var request = self.worker.editRequest();
        if (request !== undefined) {
          self.worker.selectedProductArea(request.product_area);
        }
      });
      $('#edit_client_priority').change(function () {
        var client = self.worker.editClient();
        client.client_priority = self.worker.editRequest().client_priority;
        self.worker.editClient(client);
      });

      location.hash = '#profile/requests/edit';
    };

    self.updateRequest = function () {
      /**
       * Validate users input, and sends POST request to the back-end
       */

        // define variables
      var data;
      var date;
      var request = self.worker.editRequest();

      if (request.client !== undefined) self.worker.editClient(request.client);
      if (request.product_area !== undefined) {
        self.worker.selectedProductArea(request.product_area);
      }

      if (self.worker.isDate(request.target_date)) {

        var oldDate = request.target_date;
        var dateArray = oldDate.split("-");
        date = dateArray[1] + '/' + dateArray[2] + '/' + dateArray[0];

      } else self.worker.message({error: "The date has the wrong format"});

      if (request.title.length < 3) self.worker.message({error: "Title is too short"});
      if (request.description.length < 3) self.worker.message({error: "Description is too short"});
      if (request.target_date === undefined) self.worker.message({error: "Must have a date"});
      if (Number(self.worker.editClient().client_priority) < 1) self.worker.message({error: "Must have a priority"});

      var msg = self.worker.message();

      if (msg === undefined || msg.error === undefined) {
        data = {
          id: request.id,
          title: request.title,
          description: request.description,
          client: self.worker.editClient(),
          target_date: date,
          product_area: self.worker.selectedProductArea()
        };
        request.client_priority = self.worker.editClient().client_priority;
        request.client = self.worker.editClient();
        request.product_area = self.worker.selectedProductArea();
        self.worker.editRequest(request);

        self.worker.location.post('/requests/edit', data,
          function (res) {
            if (res.error) {
              self.worker.message({error: res.error});
            }
            else {
              self.worker.requests(res);
              self.worker.message({info: "Request was updated"});
              location.hash = '#profile/requests';
            }
          }, self.err)
      }
    };

    self.tooltip = function () {
      /** Checks that device is not touch type, if not run tooltip. */
      if ('ontouchstart' in document.documentElement) {
        // Block tooltip event on touch devices
        return null;
      } else {
        $('.tltip').tooltip();
      }
    }
  };

  $(document).ready(function () {
    /**
     * When page is loaded display content and run tooltip method
     */
    $('#body').removeClass('hide');
    if ('ontouchstart' in document.documentElement) {
      // Block tooltip event on touch devices
      return null;
    } else {
      $('.tltip').tooltip();
    }
  });

  ko.applyBindings(new ViewModel());
}());
