
/**
 * Send a POST request for JSON data.
 * @param {String}   url      Url address for POST.
 * @param {Object}   params   Optional parameters as an object.
 * @param {Function} callback Callback function for applying the response.
 */
var post = function (url, params, callback) {
    'use strict';
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState !== 4) {
            return;
        }
        callback(JSON.parse(xmlhttp.response));
    };
    xmlhttp.open('POST', url, true);
    xmlhttp.setRequestHeader('Content-type', 'application/json');
    xmlhttp.send(ko.toJSON(params));
};


/**
 * Send a GET request for JSON data.
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
 * Send a PUT request for JSON data.
 * @param {String}   url      Url address for POST.
 * @param {Object}   params   Optional parameters as an object.
 * @param {Function} callback Callback function for applying the response.
 */
var aput = function (url, params, callback) {
    'use strict';
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState !== 4) {
            return;
        }
        callback(JSON.parse(xmlhttp.response));
    };
    xmlhttp.open('PUT', url, true);
    xmlhttp.setRequestHeader('Content-type', 'application/json');
    xmlhttp.send(ko.toJSON(params));
};


/**
 * Send a DELETE request for JSON data.
 * @param {String}   url      Url address for POST.
 * @param {Object}   params   Optional parameters as an object.
 * @param {Function} callback Callback function for applying the response.
 */
var adel = function (url, params, callback) {
    'use strict';
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState !== 4) {
            return;
        }
        callback(JSON.parse(xmlhttp.response));
    };
    xmlhttp.open('DELETE', url, true);
    xmlhttp.setRequestHeader('Content-type', 'application/json');
    xmlhttp.send(ko.toJSON(params));
};
