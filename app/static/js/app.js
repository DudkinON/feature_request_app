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

  };

}());
