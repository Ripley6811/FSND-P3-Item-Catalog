
/**
 * Send a request for JSON data.
 * @param {String}   url      Url address for POST.
 * @param {Object}   params   Optional parameters as an object.
 * @param {Function} callback Callback function for applying the response.
 */
var post = function (url, params, callback) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState !== 4) return;
        callback(JSON.parse(xmlhttp.response));
    };
    xmlhttp.open('POST', url, true);
    xmlhttp.setRequestHeader('Content-type', 'application/json');
    xmlhttp.send(ko.toJSON(params));
};


/**
 * Send a request for JSON data.
 * @param {String}   url      Url address for POST.
 * @param {Object}   params   Optional parameters as an object.
 * @param {Function} callback Callback function for applying the response.
 */
var aget = function (url, params, callback) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState !== 4) return;
        callback(JSON.parse(xmlhttp.response));
    };
    url += '?';
    params = ko.toJSON(params);
    for (key in params) {
        url += key + '=' + params[key]; 
    }
    xmlhttp.open('GET', url, true);
    xmlhttp.send();
};