/**
 * Send an AJAJ GET request.
 * @param {String}   url      Url address for POST.
 * @param {Object}   params   Optional parameters as an object.
 * @param {Function} callback Callback function for applying the response.
 */
var aget = function (url, params, callback) {
    'use strict';
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState !== 4) {
            return;
        }
        callback(JSON.parse(xmlhttp.response));
    };
    params = ko.toJS(params);
    // Change params into a list of strings and join with URL.
    var param_list = [];
    for (var key in params) {
        param_list.push(key + '=' + params[key]);
    }
    if (param_list.length > 0) {
        url += '?' + param_list.join('&');
    }
    xmlhttp.open('GET', url, true);
    xmlhttp.send();
};


/**
 * Send an AJAJ request.
 * @param {String}   method   AJAJ method for http request.
 * @param {String}   url      Url address for http request.
 * @param {Object}   params   Optional parameters as an object.
 * @param {Function} callback Callback function for applying the response.
 */
var sendJSON = function (method, url, params, callback) {
    'use strict';
    var test = ['POST', 'DELETE', 'PUT'].indexOf(method)
    if (test >= 0) {
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function () {
            if (xmlhttp.readyState !== 4) {
                return;
            }
            callback(JSON.parse(xmlhttp.response));
        };
        xmlhttp.open(method, url, true);
        xmlhttp.setRequestHeader('Content-type', 'application/json');
        xmlhttp.send(ko.toJSON(params));
    }
}


/**
 * Send an AJAJ POST request.
 * @param {String}   url      Url address for POST.
 * @param {Object}   params   Optional parameters as an object.
 * @param {Function} callback Callback function for applying the response.
 */
var post = function (url, params, callback) {
    'use strict';
    sendJSON('POST', url, params, callback);
};


/**
 * Send an AJAJ PUT request.
 * @param {String}   url      Url address for POST.
 * @param {Object}   params   Optional parameters as an object.
 * @param {Function} callback Callback function for applying the response.
 */
var aput = function (url, params, callback) {
    'use strict';
    sendJSON('PUT', url, params, callback);
};


/**
 * Send an AJAJ DELETE request.
 * @param {String}   url      Url address for POST.
 * @param {Object}   params   Optional parameters as an object.
 * @param {Function} callback Callback function for applying the response.
 */
var adel = function (url, params, callback) {
    'use strict';
    sendJSON('DELETE', url, params, callback);
};
